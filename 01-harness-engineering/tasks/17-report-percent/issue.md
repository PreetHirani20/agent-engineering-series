The weekly report shows `Conversion: 4500.0%` for a week with 450 signups and 1,000 visits. It should say `Conversion: 45.0%`.

Also, for a week with no visits at all, `weekly_report()` crashes with `ZeroDivisionError`. It should show `0.0%` for both the conversion rate and the bounce rate.

Other parts of the analytics package (the dashboard, the formatting helpers) are correct today and must keep working.
