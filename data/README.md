# Sample Data

Test data for the Japanese company search engine.

## Files

**`sample_companies.csv`** - 25 Japanese companies across 9 prefectures covering AI/ML, software, mobile, IoT, healthcare, manufacturing, fintech, and gaming.

**`whoosh_index/`** - Pre-built search index for immediate testing.

## Coverage

**Industries:** AI/ML (4), Software (6), Mobile (3), IoT (3), Healthcare (2), Manufacturing (3), Fintech (2), Gaming (1), Sustainability (1)

**Prefectures:** Tokyo (7), Osaka (4), Fukuoka (4), Aichi (4), Kanagawa (2), Others (4)

## Loading Data

```bash
# Create index from sample CSV
python scripts/create_index.py data/sample_companies.csv
```

## Test Queries

**Keywords:** Python, AI, 機械学習, IoT, 医療, 製造業, 金融

**Prefecture filters:** tokyo (7), osaka (4), fukuoka (4), aichi (4)

**Mixed queries:** "Python 開発", "AI システム"