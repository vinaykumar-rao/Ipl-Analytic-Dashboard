"""Season-specific remote photos. Attribution and source are in README.md."""
SOURCE = 'https://news24online.com/photos/sports/from-rr-to-rcb-ipl-winners-since-2008-revealed-mi-and-csk-won-it-five-times-three-time-champions-were-kkr-849640'
_FILES = {
    2008: '142534.087', 2009: '142708.170', 2010: '142843.128',
    2011: '142955.461', 2012: '143153.895', 2013: '143339.279',
    2014: '143447.901', 2015: '143724.308', 2016: '143826.901',
    2017: '143951.637', 2018: '144127.920', 2019: '144342.050',
    2020: '151556.134', 2021: '151726.298', 2022: '152009.039',
    2023: '152155.217', 2024: '152534.021',
}
PHOTOS = {year: f'https://news24online.com/wp-content/uploads/2026/05/Untitled-design-2026-05-28T{file}.jpg?w=735'
          for year, file in _FILES.items()}
