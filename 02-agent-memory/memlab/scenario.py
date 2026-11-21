"""Eight weeks in the life of an operations agent, with tasks that need memory.

The agent works for Fern & Flour, a small online shop selling baking supplies. Every working
day (a "session") it sees owner notes, customer and supplier emails, and tool outputs. A few
messages carry facts it will need weeks later; most are routine noise. Some facts change, one
offer expires, a discount is withdrawn, and one customer asks for their phone number to be deleted.

`generate(seed)` builds the same timeline with different names and values for each seed. Every task
records the events that answer it (its evidence) and any older values that would now be wrong.
"""

from __future__ import annotations

import random
import zlib
from dataclasses import dataclass, field
from datetime import date, timedelta

SESSIONS = 40  # eight working weeks
START = date(2026, 9, 7)  # a Monday
SHOP = "Fern & Flour"
OWNER = "Sam (owner)"


@dataclass
class Event:
    id: str
    session: int
    day: date
    source: str
    text: str

    def render(self) -> str:
        return f"[{self.day:%a %d %b}] {self.source}: {self.text}"


@dataclass
class Task:
    id: str
    session: int
    day: date
    fact: str
    category: str  # recall | update | expired | deleted
    prompt: str
    field: str
    kind: str  # how the answer is compared: text | carrier | number | postcode | email | code | time
    expected: object  # None means "we should not have this any more"
    old_values: list = field(default_factory=list)  # values that used to be right
    confusers: list = field(default_factory=list)  # right values for a different customer
    evidence: list[str] = field(default_factory=list)  # event ids that answer it
    stated_session: int = 0  # when the current value was last stated


@dataclass
class Scenario:
    seed: int
    days: list[date]
    sessions: list[list[Event]]
    tasks: list[Task]
    forget: list[str]  # strings a customer asked us to delete

    def events_until(self, session: int) -> list[Event]:
        return [e for s in self.sessions[: session + 1] for e in s]


def working_days(n: int) -> list[date]:
    days, d = [], START
    while len(days) < n:
        if d.weekday() < 5:
            days.append(d)
        d += timedelta(days=1)
    return days


CITIES = [
    ("Leeds", "LS"), ("Bristol", "BS"), ("York", "YO"), ("Brighton", "BN"), ("Norwich", "NR"),
    ("Bath", "BA"), ("Exeter", "EX"), ("Durham", "DH"), ("Cardiff", "CF"), ("Oxford", "OX"),
    ("Cambridge", "CB"), ("Sheffield", "S"), ("Nottingham", "NG"), ("Glasgow", "G"),
    ("Edinburgh", "EH"), ("Manchester", "M"), ("Leicester", "LE"), ("Reading", "RG"),
]
STREETS = ["Mill Lane", "Church Road", "Orchard Close", "Station Road", "Victoria Street", "Park Avenue",
           "Kings Road", "Bridge Street", "Meadow Way", "High Street", "Elm Grove", "Queens Terrace"]
FIRST = ["Priya", "Tom", "Aisha", "Ben", "Chloe", "Daniel", "Ella", "Farah", "George", "Hana", "Isaac",
         "Jade", "Kofi", "Laura", "Mohammed", "Nina", "Oscar", "Rosa", "Samir", "Tess", "Usman", "Vera",
         "Will", "Yara", "Zoe", "Ravi", "Megan", "Leon", "Imogen", "Callum"]
LAST = ["Patel", "Hughes", "Khan", "Walsh", "Murphy", "Okafor", "Clarke", "Novak", "Reid", "Silva",
        "Turner", "Byrne", "Ahmed", "Price", "Lund", "Moreau", "Kaur", "Evans", "Doyle", "Bianchi"]
# The customer whose details change, and a second customer with the same surname.
LOOKALIKES = [("Lena", "Sofia"), ("Anna", "Marta"), ("Jon", "Erik"), ("Katrin", "Ingrid"), ("Nils", "Henrik")]
LOOKALIKE_LAST = ["Fischer", "Berg", "Larsen", "Hoffman", "Novak"]
UK_CARRIERS = ["Royal Mail", "Evri", "DPD", "Parcelforce", "Yodel"]
EU_CARRIERS = ["DHL Express", "UPS", "FedEx", "GLS"]
SUPPLIERS = [("Millbrook Flour", "millbrookflour.co.uk"), ("Harrow Mills", "harrowmills.co.uk"),
             ("Oakfield Grain", "oakfieldgrain.co.uk"), ("Stoneground & Co", "stoneground.co.uk")]
PRODUCTS = ["Strong white flour", "Wholemeal flour", "Rye flour", "Spelt flour", "Oat flour", "Oat bran",
            "Jumbo oats", "Buckwheat flour", "Semolina", "Cornflour", "Rice flour", "Chickpea flour",
            "Malted grain flour", "Pizza flour 00"]
SHOP_SKUS = ["Sourdough starter kit", "Banneton 1kg", "Dough scraper", "Proving basket 500g", "Bread lame",
             "Pastry brush", "Rolling pin beech", "Baking stone", "Oven thermometer", "Piping bags x50",
             "Vanilla pods x3", "Cocoa powder 500g", "Caster sugar 1kg", "Dark chocolate drops", "Yeast sachets x12",
             "Silicone mat", "Loaf tin 2lb", "Cooling rack", "Digital scale", "Sprinkles mix", "Almond flour 1kg",
             "Muscovado sugar", "Cake tin 8in", "Tart tin 9in", "Measuring cups", "Spatula set", "Food colouring set",
             "Muffin cases x100", "Gluten-free flour 1kg", "Rye flour 1kg", "Spelt flour 1kg", "Oat flour 1kg",
             "Strong white flour 1.5kg", "Wholemeal flour 1.5kg", "Pizza flour 00 1kg", "Dough whisk"]
CODE_WORDS = ["CRUMB", "KNEAD", "THANKS", "LOYAL", "RISE", "BAKER", "DOUGH", "FERN"]
CHAT = [
    "The market stall on Saturday went well, sold out of starter kits by noon.",
    "I'm at the dentist Thursday morning, so I'll check messages after lunch.",
    "Can you remind me to renew the domain before the end of the month?",
    "The photographer is coming next week for the new product shots.",
    "Packing table is wobbly again, I'll fix it this afternoon.",
    "Great reviews this week, someone called our rye flour 'life changing'.",
    "We're low on tape, I've ordered more.",
    "I'm thinking about a bread-making workshop in spring. Nothing to do yet.",
    "Instagram post about the banneton got lots of comments.",
    "The printer is jammed, labels will be a bit late today.",
    "Please don't reply to the spam email about SEO services.",
    "Coffee machine is broken, productivity may drop.",
]


class Builder:
    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        self.seed = seed
        self.days = working_days(SESSIONS)
        self.sessions: list[list[Event]] = [[] for _ in range(SESSIONS)]
        self.tasks: list[Task] = []
        self.ids = 0

    def say(self, s: int, source: str, text: str) -> str:
        self.ids += 1
        eid = f"e{self.ids:04d}"
        self.sessions[s].append(Event(eid, s, self.days[s], source, text))
        return eid

    def ask(self, s: int, fact: str, category: str, prompt: str, field: str, kind: str, expected,
            old=(), evidence=(), stated=0, confusers=()) -> None:
        tid = f"s{self.seed}-{len(self.tasks) + 1:02d}-{fact}"
        self.tasks.append(Task(tid, s, self.days[s], fact, category, prompt, field, kind, expected,
                               list(old), list(confusers), list(evidence), stated))

    def postcode(self, area: str) -> str:
        r = self.rng
        letters = "ABDEFGHJLNPQRSTUWXYZ"
        return f"{area}{r.randint(1, 19)} {r.randint(1, 9)}{r.choice(letters)}{r.choice(letters)}"

    def person(self) -> str:
        return f"{self.rng.choice(FIRST)} {self.rng.choice(LAST)}"


def generate(seed: int) -> Scenario:
    b = Builder(seed)
    r = b.rng

    # ---- the values this seed uses ------------------------------------------------------------
    c1, c2, c3 = r.sample(UK_CARRIERS, 3)
    eu = r.choice(EU_CARRIERS)
    returns_old, returns_new = r.choice([14, 28, 30]), r.choice([45, 60, 90])
    ship_base, ship_promo = r.choice([40, 50, 60]), r.choice([20, 25, 30])
    cut_h, cut_m = r.choice([(13, 0), (14, 0), (15, 30), (16, 0)])
    first_a, first_b = r.choice(LOOKALIKES)
    surname = r.choice(LOOKALIKE_LAST)
    cust_a, cust_b = f"{first_a} {surname}", f"{first_b} {surname}"
    (city1, a1), (city2, a2), (city3, a3) = r.sample(CITIES, 3)
    pc1, pc2, pc3 = b.postcode(a1), b.postcode(a2), b.postcode(a3)
    st1, st2, st3 = r.sample(STREETS, 3)
    phone = f"07700 900{r.randint(100, 999)}"
    supplier, domain = r.choice(SUPPLIERS)
    rep1, rep2 = b.person(), b.person()
    email1 = f"{rep1.split()[0].lower()}@{domain}"
    email2 = f"{rep2.split()[0].lower()}.{rep2.split()[1].lower()}@{domain}"
    account = f"{''.join(w[0] for w in supplier.replace('&', '').split())}-{r.randint(10000, 99999)}"
    w1, w2 = r.sample(CODE_WORDS, 2)
    code1, code2 = f"{w1}{r.choice([10, 15])}", f"{w2}{r.choice([12, 20])}"
    price_old = round(r.uniform(1.05, 1.45), 2)
    price_new = round(price_old + r.choice([0.10, 0.15, 0.20, 0.25]), 2)
    cut_text = f"{cut_h % 12 or 12}{':' + str(cut_m) if cut_m else ''}{'pm' if cut_h >= 12 else 'am'}"
    other_supplier = ("BoxCo Packaging", "boxco.co.uk")
    box_rep = b.person()

    def price_list(s: int, oat_price: float) -> str:
        rows = []
        for p in PRODUCTS:
            h = zlib.crc32(f"{seed}:{p}".encode())
            price = oat_price if p == "Oat flour" else round(0.6 + (h % 120) / 100, 2)
            rows.append(f"{p:<20} | 25kg sack | £{price:.2f}/kg | lead time {2 + h % 4} days")
        return (f"Price list attached for {SHOP} (account holders). Prices per kg, ex VAT.\n"
                + "product              | pack      | price      | lead time\n" + "\n".join(rows))

    # ---- facts: said once, changed, expired, deleted -----------------------------------------
    ev = {}
    ev["cutoff"] = b.say(0, OWNER, f"Setup notes for you. Courier collection is at {cut_text} every day; "
                         "anything packed after that goes out the next working day.")
    ev["uk1"] = b.say(0, OWNER, f"UK parcels go with {c1}. Use their tracked 48 service.")
    ev["ret1"] = b.say(0, OWNER, f"Our returns window is {returns_old} days from delivery.")
    ev["ship1"] = b.say(0, OWNER, f"Free UK shipping on orders over £{ship_base}.")
    ev["eu"] = b.say(1, OWNER, f"Orders to the EU always go with {eu}, tracked and duties paid. Never anything else for EU.")
    ev["acct"] = b.say(1, OWNER, f"Our wholesale account number with {supplier} is {account}. "
                       "They reject any purchase order without it.")
    ev["addr1"] = b.say(2, f"Email from {cust_a}", f"Hi! I'm a new wholesale customer (small cafe). Please send "
                        f"all my orders to 14 {st1}, {city1} {pc1}. If the courier needs me, my mobile is {phone}.")
    ev["rep1"] = b.say(3, f"Email from {supplier}", f"Hello, I'm {rep1}, your account manager. "
                       f"Please send purchase orders to {email1}.")
    ev["custb"] = b.say(4, f"Email from {cust_b}", f"Hello, please deliver my order to 3 {st3}, {city3} {pc3}. Thanks!")
    ev["price1"] = b.say(5, f"Email from {supplier}", price_list(5, price_old))
    ev["code1"] = b.say(6, OWNER, f"Loyal customers (5+ orders) get the code {code1} for 15% off. "
                        "Give it out when they ask.")
    ev["del"] = b.say(11, f"Email from {cust_a}", "Could you please remove my phone number from your records? "
                      "I don't want to be contacted by phone or text. Email is fine.")
    ev["uk2"] = b.say(13, OWNER, f"{c1} lost three parcels last week. From today UK orders go with {c2} instead.")
    ev["rep2"] = b.say(15, f"Email from {supplier}", f"{rep1} has left the company. Your new account manager is "
                       f"{rep2}; please send purchase orders to {email2} from now on.")
    ev["ret2"] = b.say(17, OWNER, f"We're extending the returns window to {returns_new} days from delivery, starting today.")
    ev["addr2"] = b.say(18, f"Email from {cust_a}", f"We've moved the cafe! New delivery address: 7 {st2}, "
                        f"{city2} {pc2}. Please use this for all future orders.")
    ev["code2"] = b.say(19, OWNER, f"Someone posted {code1} on a coupon site. It's retired. "
                        f"Loyal customers get {code2} instead now.")
    friday = b.days[24]
    ev["ship2"] = b.say(20, OWNER, f"Autumn promo: this week only, until Friday {friday:%d %b}, free UK shipping "
                        f"starts at £{ship_promo}. After that it goes back to normal.")
    ev["price2"] = b.say(24, f"Email from {supplier}", "Updated prices from today, sorry about the increase.\n"
                         + price_list(24, price_new))
    ev["uk3"] = b.say(26, OWNER, f"{c2} has been a mess too. Switch UK orders to {c3} from now on.")
    ev["code3"] = b.say(28, OWNER, "We're ending loyalty discounts completely, starting today. "
                        "Don't give out any discount codes from now on.")

    # ---- tasks ------------------------------------------------------------------------------
    ship_task = "A customer in {city} wants to know if their order of £{amount} qualifies for free UK shipping. What is the free-shipping threshold in pounds right now?"
    b.ask(6, "phone", "recall", f"The courier needs a contact number for {cust_a}'s parcel. What phone number do we have on file for them?",
          "phone", "text", phone, evidence=[ev["addr1"]], stated=2)
    b.ask(8, "uk_carrier", "recall", "Create a shipping label for a new order going to Leeds. Which carrier do we use?",
          "carrier", "carrier", c1, evidence=[ev["uk1"]], stated=0)
    b.ask(9, "returns", "recall", "A customer asks how long they have to return an item. How many days is our returns window?",
          "days", "number", returns_old, evidence=[ev["ret1"]], stated=0)
    b.ask(10, "address", "recall", f"Create a shipping label for {cust_a}'s new order. What postcode does it go to?",
          "postcode", "postcode", pc1, confusers=[pc3], evidence=[ev["addr1"]], stated=2)
    b.ask(12, "supplier_email", "recall", f"Send a purchase order to our flour supplier, {supplier}. Which email address does it go to?",
          "email", "email", email1, evidence=[ev["rep1"]], stated=3)
    b.ask(14, "oat_price", "recall", f"Draft a purchase order to {supplier} for 200 kg of oat flour. What unit price per kg do we expect to pay, in pounds?",
          "price_per_kg", "number", price_old, evidence=[ev["price1"]], stated=5)
    b.ask(16, "discount", "recall", "A loyal customer with 8 orders asks for their discount code. Which code do we give them? Use null if we don't give one.",
          "code", "code", code1, evidence=[ev["code1"]], stated=6)
    b.ask(19, "uk_carrier", "update", "Create a shipping label for a new order going to Bristol. Which carrier do we use?",
          "carrier", "carrier", c2, old=[c1], evidence=[ev["uk1"], ev["uk2"]], stated=13)
    b.ask(22, "free_shipping", "update", ship_task.format(city="Bath", amount=ship_promo + 4),
          "threshold", "number", ship_promo, old=[ship_base], evidence=[ev["ship1"], ev["ship2"]], stated=20)
    b.ask(25, "discount", "update", "A loyal customer with 6 orders asks for their discount code. Which code do we give them? Use null if we don't give one.",
          "code", "code", code2, old=[code1], evidence=[ev["code1"], ev["code2"]], stated=19)
    b.ask(29, "returns", "update", "A customer asks how long they have to return an item. How many days is our returns window?",
          "days", "number", returns_new, old=[returns_old], evidence=[ev["ret1"], ev["ret2"]], stated=17)
    b.ask(30, "address", "update", f"Create a shipping label for {cust_a}'s latest order. What postcode does it go to?",
          "postcode", "postcode", pc2, old=[pc1], confusers=[pc3], evidence=[ev["addr1"], ev["addr2"]], stated=18)
    b.ask(31, "supplier_email", "update", f"Send a purchase order to our flour supplier, {supplier}. Which email address does it go to?",
          "email", "email", email2, old=[email1], evidence=[ev["rep1"], ev["rep2"]], stated=15)
    b.ask(33, "uk_carrier", "update", "Create a shipping label for a new order going to York. Which carrier do we use?",
          "carrier", "carrier", c3, old=[c1, c2], evidence=[ev["uk1"], ev["uk2"], ev["uk3"]], stated=26)
    b.ask(33, "free_shipping", "expired", ship_task.format(city="Leeds", amount=ship_promo + 4),
          "threshold", "number", ship_base, old=[ship_promo], evidence=[ev["ship1"], ev["ship2"]], stated=0)
    b.ask(35, "phone", "deleted", f"The courier needs a contact number for {cust_a}'s parcel. What phone number do we have on file for them? Use null if we have none.",
          "phone", "text", None, old=[phone], evidence=[ev["addr1"], ev["del"]], stated=11)
    b.ask(36, "lookalike", "recall", f"Create a shipping label for {cust_b}'s new order. What postcode does it go to?",
          "postcode", "postcode", pc3, confusers=[pc1, pc2], evidence=[ev["custb"]], stated=4)
    b.ask(37, "eu_carrier", "recall", "Create a shipping label for a new order going to Lyon, France. Which carrier do we use?",
          "carrier", "carrier", eu, evidence=[ev["eu"]], stated=1)
    b.ask(37, "discount", "expired", "A loyal customer with 9 orders asks for their discount code. Which code do we give them? Use null if we don't give one.",
          "code", "code", None, old=[code1, code2], evidence=[ev["code1"], ev["code2"], ev["code3"]], stated=28)
    b.ask(38, "cutoff", "recall", "A customer asks for the latest time they can order for same-day dispatch. What is our courier collection time (HH:MM, 24-hour)?",
          "time", "time", f"{cut_h:02d}:{cut_m:02d}", evidence=[ev["cutoff"]], stated=0)
    b.ask(38, "oat_price", "update", f"Draft a purchase order to {supplier} for 300 kg of oat flour. What unit price per kg do we expect to pay, in pounds?",
          "price_per_kg", "number", price_new, old=[price_old], evidence=[ev["price1"], ev["price2"]], stated=24)
    b.ask(39, "account", "recall", f"Fill in the header of a purchase order to {supplier}. What is our wholesale account number with them?",
          "account_number", "code", account, evidence=[ev["acct"]], stated=1)

    # ---- routine noise ----------------------------------------------------------------------
    order_id = 10400
    customers = [b.person() for _ in range(40)]
    for s in range(SESSIONS):
        rows = []
        for _ in range(r.randint(14, 20)):
            order_id += 1
            city, area = r.choice(CITIES)
            items = ", ".join(r.sample(SHOP_SKUS, r.randint(1, 3)))
            rows.append(f"#{order_id} | {r.choice(customers):<16} | {city:<10} | {items} | £{r.uniform(8, 140):.2f} | "
                        f"{r.choice(['paid', 'paid', 'paid', 'packed', 'refunded'])}")
        b.say(s, "Tool output: orders_export(today)", "order | customer | city | items | total | status\n" + "\n".join(rows))
        pages = r.sample(SHOP_SKUS, 24)
        b.say(s, "Tool output: web_analytics(yesterday)", "page | visits | add-to-cart | conversion\n" + "\n".join(
            f"/products/{p.lower().replace(' ', '-')} | {r.randint(20, 900)} | {r.randint(0, 60)} | {r.uniform(0.2, 6):.1f}%"
            for p in pages))
        stock = "\n".join(f"{sku:<26} | {r.randint(0, 240):>4} | shelf {r.choice('ABCDEF')}{r.randint(1, 9)}"
                          for sku in SHOP_SKUS)
        b.say(s, "Tool output: inventory_snapshot()", "sku | in stock | location\n" + stock)
        for _ in range(r.randint(2, 3)):
            name = r.choice(customers)
            city, area = r.choice(CITIES)
            b.say(s, f"Email from {name}", r.choice([
                f"Hi, where is my order #{r.randint(10400, order_id)}? It's going to {r.randint(1, 90)} {r.choice(STREETS)}, {city} {b.postcode(area)}.",
                "Do you sell gluten-free bread mix? Couldn't find it on the site.",
                f"My parcel arrived damaged, the {r.choice(SHOP_SKUS).lower()} was cracked. What should I do?",
                "Can I change the delivery address on my order? It's the same street, different house number.",
                "Loved the starter kit! Any tips for a first sourdough?",
                "Is the banneton dishwasher safe?",
            ]))
        if r.random() < 0.5:
            b.say(s, OWNER, r.choice(CHAT))
        if r.random() < 0.35:
            carrier = r.choice(UK_CARRIERS + EU_CARRIERS)
            b.say(s, f"Email from {carrier}", f"Hello from the {carrier} sales team. We can offer {SHOP} "
                  f"£{r.uniform(2.5, 4.5):.2f} per parcel on a 12-month contract. Reply if interested.")
        if r.random() < 0.3:
            b.say(s, f"Email from {other_supplier[0]}", f"Hi, {box_rep} here from {other_supplier[0]}. Your box order "
                  f"ships Thursday. For future orders email {box_rep.split()[0].lower()}@{other_supplier[1]}.")

    for events in b.sessions:  # facts and noise arrive in no particular order during the day
        r.shuffle(events)
    return Scenario(seed, b.days, b.sessions, sorted(b.tasks, key=lambda t: t.session), [phone])
