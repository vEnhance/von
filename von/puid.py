import hashlib
import re

from .rc import VON_CUSTOM_LOOKUP

lookup = {
    "Afghanistan": "AFG",
    "Albania": "ALB",
    "Algeria": "ALG",
    "Angola": "AGO",
    "Argentina": "ARG",
    "Armenia": "ARM",
    "Australia": "AUS",
    "Austria": "AUT",
    "Azerbaijan": "AZE",
    "Bahrain": "BAH",
    "Bangladesh": "BGD",
    "Belarus": "BLR",
    "Belgium": "BEL",
    "Benin": "BEN",
    "Bolivia": "BOL",
    "Bosnia and Herzegovina": "BIH",
    "Botswana": "BWA",
    "Brazil": "BRA",
    "Brunei": "BRU",
    "Bulgaria": "BGR",
    "Burkina Faso": "BFA",
    "Cambodia": "KHM",
    "Canada": "CAN",
    "Chile": "CHI",
    "China": "CHN",
    "Colombia": "COL",
    "Commonwealth of Independent States": "CIS",
    "Costa Rica": "CRI",
    "Croatia": "HRV",
    "Cuba": "CUB",
    "Cyprus": "CYP",
    "Czech": "CZE",
    "Czechoslovakia": "CZS",
    "Denmark": "DEN",
    "Dominican Republic": "DOM",
    "Ecuador": "ECU",
    "Egypt": "EGY",
    "Estonia": "EST",
    "Finland": "FIN",
    "France": "FRA",
    "Gambia": "GMB",
    "Georgia": "GEO",
    "German Democratic Republic": "GDR",
    "Germany": "GER",
    "Ghana": "GHA",
    "Greece": "HEL",
    "Guatemala": "GTM",
    "Honduras": "HND",
    "Hong Kong": "HKG",
    "Hungary": "HUN",
    "Iceland": "ISL",
    "India": "IND",
    "Indonesia": "IDN",
    "Iraq": "IRQ",
    "Iran": "IRN",
    "Ireland": "IRL",
    "Israel": "ISR",
    "Italy": "ITA",
    "Ivory Coast": "CIV",
    "Jamaica": "JAM",
    "Japan": "JPN",
    "Kazakhstan": "KAZ",
    "Kenya": "KEN",
    "North Korea": "PRK",
    "Korea": "KOR",
    "Kosovo": "KSV",
    "Kuwait": "KWT",
    "Kyrgyzstan": "KGZ",
    "Laos": "LAO",
    "Latvia": "LVA",
    "Liechtenstein": "LIE",
    "Lithuania": "LTU",
    "Luxembourg": "LUX",
    "Macau": "MAC",
    "Macedonia": "MKD",
    "Madagascar": "MDG",
    "Malaysia": "MAS",
    "Mauritania": "MRT",
    "Mexico": "MEX",
    "Moldova": "MDA",
    "Mongolia": "MNG",
    "Montenegro": "MNE",
    "Morocco": "MAR",
    "Mozambique": "MOZ",
    "Myanmar": "MMR",
    "Nepal": "NPL",
    "Netherlands": "NLD",
    "New Zealand": "NZL",
    "Nicaragua": "NIC",
    "Nigeria": "NGA",
    "North Macedonia": "MKD",
    "Norway": "NOR",
    "Oman": "OMN",
    "Pakistan": "PAK",
    "Panama": "PAN",
    "Paraguay": "PAR",
    "Peru": "PER",
    "Philippines": "PHI",
    "Poland": "POL",
    "Portugal": "POR",
    "Puerto Rico": "PRI",
    "Romania": "ROU",
    "Russia": "RUS",
    "El Salvador": "SLV",
    "Saudi Arabia": "SAU",
    "Senegal": "SEN",
    "Serbia": "SRB",
    "Serbia and Montenegro": "SCG",
    "Singapore": "SGP",
    "Slovakia": "SVK",
    "Slovenia": "SVN",
    "South Africa": "SAF",
    "Spain": "ESP",
    "Sri Lanka": "LKA",
    "Sweden": "SWE",
    "Switzerland": "SUI",
    "Syria": "SYR",
    "Taiwan": "TWN",
    "Tajikistan": "TJK",
    "Tanzania": "TZA",
    "Thailand": "THA",
    "Trinidad and Tobago": "TTO",
    "Tunisia": "TUN",
    "Turkey": "TUR",
    "Turkmenistan": "TKM",
    "Uganda": "UGA",
    "Ukraine": "UKR",
    "United Arab Emirates": "UAE",
    "United Kingdom": "UNK",
    "Uruguay": "URY",
    "Uzbekistan": "UZB",
    "Venezuela": "VEN",
    "Vietnam": "VNM",
    "Yemen": "YEM",
    "Yugoslavia": "YUG",
    "Zimbabwe": "ZWE",
}
for k, v in list(lookup.items()):
    lookup[k + " MO"] = v + "MO"
    lookup[k + " TST"] = v + "TST"
    lookup[k + " GST"] = v + "EST"  # GMO selection test
    lookup[k + " RMM TST"] = v + "RST"
    lookup[k + " EGMO TST"] = v + "EST"
    lookup[k + " JBMO TST"] = v + "JST"
    lookup[k + " TSTST"] = v + "TSTST"

lookup["AMC 10A"] = "10A"
lookup["AMC 10B"] = "10B"
lookup["AMC 12A"] = "12A"
lookup["AMC 12B"] = "12B"
lookup["ARML Local"] = "ARMLOC"
lookup["Athemath"] = "ATHE"
lookup["Balkan"] = "BALK"
lookup["Baltic Way"] = "BWAY"
lookup["Brazil Revenge"] = "BRAR"
lookup["Brazil Undergrad"] = "BRAU"
lookup["Catalunya"] = "CTLNYA"
lookup["Centroamerican"] = "CENTRO"
lookup["China TST Quiz"] = "CHNQ"
lookup["CodeForces"] = "CF"
lookup["Cono Sur"] = "CSUR"
lookup["Cyberspace Competition"] = "CYBER"
lookup["Czech Polish Slovak"] = "CPS"
lookup["December TST"] = "DECTST"
lookup["ELMO Revenge"] = "ELMOR"
lookup["ELMO SL"] = "ESL"
lookup["European Cup"] = "EURCUP"
lookup["HMMT"] = "HMMT"
lookup["Feb HMMT IntBee"] = "FEBIB"
lookup["Nov HMMT IntBee"] = "NOVIB"
lookup["CMM IntBee"] = "CMMIB"
lookup["IntBee Quals"] = "MIBQT"
lookup["IntBee"] = "MITIB"
lookup["HMNT"] = "HMNT"
lookup["Iberoamerican"] = "IBERO"
lookup["InftyDots"] = "IDOTS"
lookup["January TST"] = "JANTST"
lookup["KoMaL"] = "KML"
lookup["Korea Winter"] = "KORW"
lookup["Korea Summer"] = "KORS"
lookup["Kurschak"] = "KSK"
lookup["Longlist"] = "LL"
lookup["math.SE"] = "MSE"
lookup["Mathematical Reflections"] = "MR"
lookup["MathOverflow"] = "OVFW"
lookup["MathDash"] = "MD"
lookup["Math Prize"] = "MPO"
lookup["MP4G"] = "MP4G"
lookup["Napkin"] = "NAP"
lookup["NIMO Winter"] = "NIMOW"
lookup["PUMaC Finals"] = "PUF"
lookup["Putnam"] = "PTNM"
lookup["Rioplatense"] = "RPTN"
lookup["Schweitzer"] = "MSZ"
lookup["Serbia RMM TST"] = "SRBRST"
lookup["Sharygin"] = "SHRG"
lookup["Shortlist"] = "SL"
lookup["St Petersburg"] = "SPBRG"
lookup["Taiwan Quiz"] = "TWNQ"
lookup["ToT Fall"] = "TTF"
lookup["ToT Spring"] = "TTS"
lookup["Tuymaada"] = "TMD"
lookup["Twitch"] = "TWCH"
lookup["USAMO"] = "AMO"
lookup["USAMTS"] = "USMT"
lookup["USA GST"] = "USAEST"

lookup.update(VON_CUSTOM_LOOKUP)
# whooooo
REGEX = r"(?P<contest>[a-zA-Z][a-zA-Z0-9 ]+)(19|20)(?P<year>[0-9][0-9])(?P<stem>[ \/](?P<locator>[0-9A-Za-z\.\/\- ]+))?$"
re_generic = re.compile(REGEX)

sorted_lookup_keys = list(lookup.keys())
sorted_lookup_keys.sort(key=lambda x: (-len(x), x))


def getOnlyAlphanum(s: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", s.upper())


def inferPUID(source: str) -> str:
    source = source.replace("Finals", "F")
    if (m := re_generic.match(source)) is not None:
        d = m.groupdict()
        contest = d["contest"].strip()
        source = (
            d["year"]
            + lookup.get(contest, getOnlyAlphanum(contest))
            + getOnlyAlphanum(d["stem"] or "")
        )
        if contest in lookup:
            return source
        thresh = 11
    elif source[0] == "H" and source[1:].isdigit():
        return source
    else:
        for k in sorted_lookup_keys:
            if source.startswith(k):
                source = lookup[k] + source[len(k) :]
                thresh = 11
                break
        else:
            thresh = 8
    source = getOnlyAlphanum(source)
    if len(source) <= thresh:
        return source
    else:
        # still too long, return some sort of hash
        return "Z" + (hashlib.sha256(source.encode("ascii")).hexdigest())[0:7].upper()
