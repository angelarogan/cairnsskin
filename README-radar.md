# Cairns Skin Question Radar

This automation gathers:

- Cairns-localised Google Autocomplete suggestions from DataForSEO
- Actual search queries and performance data from Google Search Console
- A scored CSV report
- A readable Markdown summary of the strongest content opportunities

## Required GitHub repository secrets

The repository must contain these three Actions secrets:

- `DATAFORSEO_LOGIN`
- `DATAFORSEO_PASSWORD`
- `GOOGLE_SERVICE_ACCOUNT_JSON`

Add them under:

`Repository > Settings > Secrets and variables > Actions`

## Files created by the automation

After a successful run, the workflow creates:

- `reports/latest.csv`
- `reports/daily/YYYY-MM-DD.csv`
- `reports/content-opportunities.md`

## Run it manually

1. Open the repository in GitHub.
2. Select **Actions**.
3. Select **Cairns Skin Question Radar**.
4. Select **Run workflow**.
5. Run it on the `main` branch.

## Automatic schedule

The workflow runs daily at approximately **6:30 am Queensland time**.

GitHub scheduled workflows can occasionally begin a little later during busy periods.

## Important checks

### Search Console property format

The script uses:

`https://cairnsskin.com.au/`

This is a URL-prefix property, not a Domain property. This is confirmed,
not a guess: cairnsskin.com.au was verified in Search Console using the
HTML-file method, and Google only supports that verification method for
URL-prefix properties (Domain properties require DNS TXT verification
instead), so the property must be URL-prefix.

If this ever changes (for example, if the property is re-verified via DNS
as a Domain property), override it without editing the script by setting
an optional `GSC_SITE_URL` secret/variable to the new value, which the
script reads in preference to its built-in default.

### DataForSEO account balance

DataForSEO requires available account credit. The current script makes one
Autocomplete request for each seed search.

### Google service account

The service account email must be added under:

`Search Console > Settings > Users and permissions`

It should have access to the `cairnsskin.com.au` property.

## Keep the JSON key private

Never upload the downloaded Google JSON key as a normal repository file.

It should exist only inside the encrypted GitHub secret named:

`GOOGLE_SERVICE_ACCOUNT_JSON`

After confirming that secret works, store the original JSON securely or delete
the local downloaded copy.
