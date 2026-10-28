# Offentliga menyträd: svenska myndigheter

Kartläggningen bygger på myndigheternas publika webbplatser, kontrollerade 28 oktober 2026. Träden beskriver webbplatsens synliga ämnesstruktur. De är användbara som frö för kandidatord och testfall i IVR Explorer, men visar inte telefonrobotens interna meny eller vokabulär.

## Försäkringskassan (FK)

```text
Försäkringskassan
├── Privatperson
│   ├── Familj och barn
│   │   ├── Föräldraledig
│   │   │   ├── Föräldrapenning
│   │   │   └── 10-dagar efter födsel eller adoption
│   │   ├── Vård av sjukt barn
│   │   │   ├── Vabba
│   │   │   ├── Vab när barnet fyllt 12 år
│   │   │   └── Vab – allvarligt sjuka barn
│   │   └── Andra situationer och ersättningar
│   │       ├── Barn med funktionsnedsättning / extra stöd
│   │       ├── Bostadsbidrag för barnfamiljer
│   │       ├── Föräldrar som inte lever ihop
│   │       ├── Barnbidrag och flerbarnstillägg
│   │       └── Gravid och kan inte jobba
│   ├── Sjuk eller skadad
│   │   ├── Sjukpenning
│   │   ├── Avsluta, förlänga eller ändra sjukpenning
│   │   ├── Sjuk ofta (många karensdagar)
│   │   ├── Resor till jobbet
│   │   ├── Arbetsskada
│   │   ├── Förebyggande sjukpenning / rehabilitering
│   │   ├── Närstående är svårt sjuk
│   │   └── Smittad av allmänfarlig sjukdom
│   ├── Arbetssökande
│   │   ├── Aktivitetsstöd / utvecklingsersättning i AF-program
│   │   ├── Etableringsersättning / barntillägg
│   │   ├── Ersättning för etableringsjobb
│   │   ├── Bostadsbidrag
│   │   ├── Arbetssökande med barn
│   │   └── Sjukpenning för arbetssökande
│   ├── Vuxen med funktionsnedsättning
│   │   ├── Aktivitetsersättning
│   │   ├── Sjukersättning
│   │   ├── Assistansersättning
│   │   ├── Merkostnadsersättning
│   │   ├── Bilstöd
│   │   ├── Arbetshjälpmedel
│   │   └── Bostadstillägg
│   ├── Ersättningar A–Ö
│   ├── E-tjänster, blanketter och intyg
│   ├── Mina sidor / inloggning
│   └── Kundcenter för privatperson
├── Arbetsgivare
│   ├── E-tjänster
│   │   ├── Sjukanmäl medarbetare
│   │   ├── Lämna uppgift om inkomst
│   │   └── Lämna uppgift om frånvaro
│   ├── Sjukdom och skada / sjuklön / rehabilitering
│   ├── Förebygga sjukfrånvaro
│   ├── Föräldraledighet och vab
│   ├── Ersättningar för arbetsgivare
│   ├── Blanketter
│   └── Kundcenter för partner
└── Sidor för samarbetspartner
    ├── Hälso- och sjukvård
    ├── Tandvård
    └── Myndigheter och andra samarbetspartner
```

Huvudingången för privatpersoner och de fyra ämnesgrenarna ovan syns på [FK:s privatpersonssida](https://www.forsakringskassan.se/privatperson). Undersidorna utvecklar ämnena. FK:s [termbank](https://www.forsakringskassan.se/om-forsakringskassan/forsakringskassans-termbank) innehåller definitioner, synonymer och översättningar för socialförsäkringstermer; den är en särskilt bra källa för kandidatyttranden, men inte ett facit över vad telefonroboten godtar.

## Arbetsförmedlingen (AF)

```text
Arbetsförmedlingen
├── För arbetssökande
│   ├── Arbetslös – vad händer nu?
│   │   ├── Skriv in dig
│   │   ├── Ersättning från a-kassa (länkas vidare till a-kassa)
│   │   ├── Planeringssamtal
│   │   ├── Kom igång med jobbsökandet
│   │   ├── Aktivitetsrapportera
│   │   ├── Meddela förändringar
│   │   └── Mina sidor / ärendestatus
│   ├── Extra stöd
│   │   ├── Stöd och program A–Ö
│   │   ├── När du deltar i program (ersättning, villkor, frånvaro)
│   │   ├── Funktionsnedsättning och ohälsa
│   │   ├── Återgång till arbete
│   │   ├── Rehabilitering
│   │   └── Blanketter
│   ├── Så hittar du jobbet
│   │   ├── Platsbanken / söka jobb
│   │   ├── Kompetensprofil
│   │   ├── Starta eget
│   │   ├── Jobba utomlands
│   │   └── Var finns jobben?
│   ├── Cv, ansökan och intervju
│   │   ├── Skriva cv
│   │   ├── Personligt brev
│   │   ├── Jobbintervju
│   │   ├── Referenser
│   │   └── Validering
│   ├── Vilket yrke passar dig?
│   ├── Arbeta i Sverige
│   ├── Vanliga frågor och svar
│   └── Kontakta oss / telefon / servicekontor
├── För arbetsgivare
│   ├── Annonsera i Platsbanken
│   ├── Söka kandidater
│   ├── Anställningsstöd
│   ├── Nystartsjobb
│   ├── Utbetalning / rekvirera
│   ├── Anmäla varsel
│   └── Rekryteringsstöd
├── För leverantörer
├── Om oss
└── Statistik och analyser
```

AF:s [sida för arbetssökande](https://arbetsformedlingen.se/for-arbetssokande) visar huvudgrenarna och snabbingångarna. [Sidan ”Arbetslös, vad händer nu?”](https://arbetsformedlingen.se/for-arbetssokande/arbetslos---vad-hander-nu) utvecklar inskrivning, a-kassa, planeringssamtal och aktivitetsrapportering. [Extra stöd](https://arbetsformedlingen.se/for-arbetssokande/extra-stod), [Så hittar du jobbet](https://arbetsformedlingen.se/for-arbetssokande/sa-hittar-du-jobbet), [Cv, ansökan och intervju](https://arbetsformedlingen.se/for-arbetssokande/cv-ansokan-och-intervju) och [För arbetsgivare](https://arbetsformedlingen.se/for-arbetsgivare) ger de övriga grenarna.

AF:s [kontaktsida för arbetssökande](https://arbetsformedlingen.se/kontakt/for-arbetssokande) säger uttryckligen att man når ett röststyrt talsvar och ska säga sitt ärende. Den anger också exempel på vad samtalet kan gälla: digitala tjänster och inskrivning, hinder till bokat möte, program/utbildningar/stöd, pågående ärenden samt yrkesval, jobbsökning och ansökan. Det är direkta teman att använda som första testkandidater.

## Polismyndigheten (icke-akut nummer 114 14)

```text
Polisen, 114 14 (icke-akuta ärenden)
├── Anmälan om brott
├── Tips om brott
├── Pass / nationellt id-kort
├── Tillstånd
├── Belastningsregisterutdrag
├── Allmän handling
├── Adress och öppettider
└── Övrigt ärende / tala med polis
```

Detta är en **ämnesstruktur från kontaktinformationen**, inte en verifierad komplett telefongren. Polisen uppger att 114 14 har röststyrt talsvar, och nämner bland annat att man kan säga ”tips”. Sidan styr också många ärenden mot e-tjänster. [Polisens telefonnummer och kontaktväg](https://polisen.se/om-polisen/kontakt/polisens-telefonnummer/). **112 är endast akutnummer och ska inte användas som testmål.**

## Kronofogden

```text
Kronofogden
├── Privatperson / egna skulder
│   ├── Mina skulder
│   ├── Förelägganden
│   ├── Betala skuld
│   ├── Löneutmätning
│   ├── Utmätning av egendom
│   └── Betalningsanmärkning / skuldupplysning
├── Betalningsföreläggande
├── Företag och fordringsägare (kandidatgren att verifiera)
├── Frågor och svar
└── Kundservice / växel
```

Kronofogdens kontaktsida länkar till dessa ämnen som vanliga ärenden, men anger inte där något komplett röststyrt menyträd. Se [Kontakta Kronofogden](https://kronofogden.se/kontakta-oss) och [Frågor och svar om utmätning](https://kronofogden.se/kontakta-oss/mejla-oss). Behandla därför grenarna som webb- och ämnesbaserade testkandidater, tills ett telefonsamtal bekräftar dem.

## Skatteverket

Skatteverket beskriver sin telefonist som röststyrd: ringaren ska kort säga vad den behöver hjälp med, vill fråga om eller beställa. Ibland kopplas personen först till ett automatiserat informationssvar; där erbjuds kö till handläggare om svaret inte räcker. Det här är en av de tydligast dokumenterade offentliga beskrivningarna av en röststyrd myndighetsingång.

```text
Skatteverket – digital telefonist
├── Säg kort vad du behöver hjälp med
│   ├── Skatt / deklaration
│   ├── Folkbokföring / anmäla ny adress
│   ├── Pågående ärende / handläggare
│   ├── Ändra konto för skatteutbetalning
│   └── Beställa / övrig fråga
├── Möjligt automatiserat informationssvar
│   ├── Få information automatiskt
│   └── Be om kö till handläggare om svaret inte räcker
└── Mina sidor / e-tjänster
```

Ämnena kommer från Skatteverkets kontakt- och röststyrningssidor. Sidornas exempel är användbara som **starter-yttranden**, inte en fullständig grammatik. [Ring Skatteverket](https://www.skatteverket.se/ring) · [Kontakta Skatteverket](https://www.skatteverket.se/omoss/kontaktaoss)

## Migrationsverket

Här är den första nivån uttryckligen publicerad som knappval. De ämnen som ligger under knappval 1 behöver väljas vidare i samtalet och webbplatsen rekommenderar att ringaren väljer det som passar bäst; den fullständiga undermenyn är inte publicerad på den granskade sidan.

```text
Migrationsverket – telefonkontakt
├── Knappval 1: allmän fråga eller fråga om ett ärende
│   └── Ytterligare val efter ärendet/frågan (inte fullständigt publicerade)
├── Knappval 2: arbetsgivare eller samtal från myndighet
└── Knappval 3: växel
    └── Kan inte svara på frågor om personliga ärenden
```

Webbplatsens ämnen ger möjliga fröord för den första grenen, exempelvis ansökan, uppehållstillstånd, medborgarskap, arbetstillstånd, asyl och väntetider. De är inte bekräftade som telefonmenyval. [Ring Migrationsverket](https://www.migrationsverket.se/Kontakta-oss/Ring-oss.html) · [Kontaktvägar för privatpersoner](https://www.migrationsverket.se/kontakta-oss/kontaktvagar-for-privatpersoner.html)

## Pensionsmyndigheten

Den publika kontaktsidan beskriver både kundservice och en separat självbetjäningstjänst som är öppen dygnet runt. Den publicerar däremot inte en komplett meny med knappval.

```text
Pensionsmyndigheten
├── Kundservice (frågor om pension)
│   ├── Allmän pension / ansökan
│   ├── Bostadstillägg
│   ├── Utbetalningar / skatt
│   └── Ärende / Mina sidor
├── Självbetjäning (dygnet runt)
│   ├── Nästa utbetalning
│   └── Beställa blanketter / informationsmaterial
├── Tolkservice
└── Servicekontor
```

Kundservice och självbetjäningens funktioner är publicerade; ämnena under kundservice är fröord baserade på FAQ och tjänster. [Kontakta Pensionsmyndigheten](https://www.pensionsmyndigheten.se/kontakta-oss/kontakta-oss)

## Statens servicecenter

Statens servicecenter har två målgrupper som bör hållas isär. Privatpersoner besöker servicekontor för vägledning i andra myndigheters tjänster. Telefonservicen på kontaktsidan gäller främst myndighetsanställda och myndighetskontakter.

```text
Statens servicecenter
├── Anställd vid myndighet
│   ├── Portalen: service- och supportärenden
│   │   ├── Felanmälan
│   │   ├── Beställning av intyg
│   │   └── Fråga / support
│   └── Telefonservice
├── Privatperson eller företagare
│   └── Besök servicekontor
│       ├── Arbetsförmedlingens tjänster
│       ├── Försäkringskassans tjänster
│       ├── Pensionsmyndighetens tjänster
│       ├── Skatteverkets tjänster
│       └── På vissa kontor: Migrationsverkets tjänster
└── Övriga frågor om Statens servicecenter
    └── Växel / registratur
```

Den granskade kontaktsidan anger telefon för myndighetsanställdas service och en separat växel, men visar ingen röststyrd privatpersonsmeny. Därför är Statens servicecenter intressant som routing mellan organisationer och ärendetyper, men mindre lämpligt som första IVR-mål. [Kontakta Statens servicecenter](https://www.statenssc.se/om-statens-servicecenter/kontakta-oss)

## CSN

CSN:s kontaktsida har en tydlig trevägsingång. Den är publicerad som webbknappar; den granskade sidan bekräftar inte att telefonen använder samma meny. En annan CSN-sida instruerar dock ringaren att säga ”slå ihop lån” för att komma till rätt telefonkö.

```text
CSN – kontakta oss
├── Bidrag och lån för studier
│   ├── Studiestöd
│   ├── Beslut och pengar
│   └── Ändra ansökan / uppgifter
├── Betala tillbaka lån eller återkrav
│   ├── Studielån
│   ├── Återkrav
│   ├── Betalningsplan / svårt att betala
│   └── Slå ihop lån
├── Annat
└── Mejla dokument
```

Kategorierna kommer från [CSN:s kontaktsida](https://www.csn.se/kontakta-oss.html); den konkreta telefonfrasen ”slå ihop lån” finns på [CSN:s sida om att slå ihop lån](https://www.csn.se/bidrag-och-lan/betala-tillbaka-studielan/sla-ihop-lan.html). Det är en publicerad formulering som kan bli kandidat till ett verkligt test.

## Förslag till IVR-testord från webbstrukturen

Det här är **testkandidater**, inte påstådda synonymer eller verifierade fraser. Börja med de kanoniska ämnesnamnen och testa sedan vardagliga varianter i separata samtal.

| Gren | Första kandidatord/fraser |
|---|---|
| FK: Vab | ”vab”, ”vabba”, ”vård av sjukt barn” |
| FK: sjuk | ”sjukpenning”, ”sjukskriven”, ”sjuk eller skadad” |
| FK: AF-program | ”aktivitetsstöd”, ”utvecklingsersättning”, ”ersättning i program” |
| FK: förälder | ”föräldrapenning”, ”föräldraledig”, ”10-dagar” |
| AF: inskrivning | ”skriva in mig”, ”inskrivning”, ”arbetslös” |
| AF: aktivitetsrapport | ”aktivitetsrapport”, ”rapportera aktiviteter”, ”sökt jobb” |
| AF: program/stöd | ”program”, ”arbetsmarknadsutbildning”, ”Rusta och matcha” |
| AF: personligt ärende | ”pågående ärende”, ”mitt ärende”, ”handläggare” |
| AF: jobbsökning | ”Platsbanken”, ”söka jobb”, ”cv”, ”jobbansökan” |
| Polisen: anmälan | ”anmälan”, ”anmäla brott”, ”stöld” |
| Polisen: tips | ”tips”, ”tipsa om brott” |
| Polisen: pass | ”pass”, ”nationellt id-kort” |
| Kronofogden: skuld | ”skuld”, ”betalning”, ”mina skulder” |
| Kronofogden: utmätning | ”löneutmätning”, ”utmätning”, ”utmätning av bil” |
| Kronofogden: föreläggande | ”betalningsföreläggande”, ”föreläggande” |
| Skatteverket: skatt | ”deklaration”, ”skatt”, ”skatteåterbäring” |
| Skatteverket: folkbokföring | ”folkbokföring”, ”ny adress”, ”flyttanmälan” |
| Skatteverket: ärende | ”pågående ärende”, ”handläggare”, ”mitt ärende” |
| Migrationsverket: ärende | ”fråga om ett ärende”, ”min ansökan”, ”uppehållstillstånd” |
| Migrationsverket: arbetsgivare/myndighet | ”arbetsgivare”, ”myndighet” |
| Pensionsmyndigheten: självbetjäning | ”nästa utbetalning”, ”beställa blankett” |
| Pensionsmyndigheten: kundservice | ”pension”, ”bostadstillägg”, ”utbetalning” |
| Statens servicecenter: myndighetsanställd | ”felanmälan”, ”intyg”, ”support” |
| CSN: studiestöd | ”bidrag och lån”, ”studiemedel”, ”studiebidrag” |
| CSN: återbetalning | ”betala tillbaka lån”, ”återkrav”, ”slå ihop lån” |

### Viktig tolkning

- Webbens kategorier är **förhandskunskap** och fröord för tester.
- Först när ett samtal ger evidens lägger vi till en observerad övergång eller hypotes i IVR-kartan.
- En kategori kan finnas på webbplatsen utan att finnas som röststyrt val. Telefonen kan också ha andra grupperingar.
- AF:s webbplats beskriver röststyrt talsvar, men ingen av de öppnade sidorna publicerar dess fullständiga telefongrammatik eller menyträd.
- Polisens kontaktinformation beskriver röststyrd väg in via 114 14, men inte den fullständiga telefonträdsstrukturen.
- Kronofogdens webbinformation ger relevanta ämnesingångar; den granskade kontaktsidan visar inte om telefonsamtalet är talstyrt eller DTMF-styrt.
- Skatteverkets kontaktsida beskriver röststyrning och ger exempel på korta yttranden, men publicerar inte hela igenkänningsgrammatiken eller alla vägar.
- Migrationsverket publicerar första knappvalsmenyn, men inte samtliga undermenyer för knappval 1.
- Pensionsmyndigheten publicerar funktioner för telefonisk självbetjäning men inte fullständiga knappval.
- Statens servicecenters offentliga telefonvägar är i första hand myndighetsservice/växel, inte en medborgar-IVR.
- CSN:s webbkontakt delar upp ärenden i tre kategorier; det ska inte antas vara telefonens meny utan separat observation.

## Rekommenderade nästa myndigheter

1. **Skatteverket** — mycket bra nästa mål: myndigheten beskriver sin digitala telefonist och ger exempel på korta ärendebeskrivningar, bland annat adressändring och konto för skatteutbetalning. [Så fungerar röststyrningen](https://www.skatteverket.se/ring).
2. **Migrationsverket** — bra test av klassiskt knappval och kontext: publicerad telefonväg har alternativ för allmänna frågor/ärenden, arbetsgivare eller myndighet, samt växel; därefter ytterligare val under alternativ 1. [Ring Migrationsverket](https://www.migrationsverket.se/Kontakta-oss/Ring-oss.html).
3. **Pensionsmyndigheten** — intressant kontrast mellan kundservice och självbetjäning dygnet runt; offentlig information nämner nästa utbetalning och beställning av blanketter. [Kontakta Pensionsmyndigheten](https://www.pensionsmyndigheten.se/kontakta-oss/kontakta-oss).
4. **CSN** — relevant för studiestöd, återbetalning och återkrav. Kontaktflödet delar ärenden i bidrag/lån för studier, återbetalning/återkrav och annat; verifiera först vilken telefonkanal som finns. [Kontakta CSN](https://www.csn.se/kontakta-oss.html).
5. **Statens servicecenter** — bra för senare studier av support- och myndighetsrouting. Den publika telefonservicen riktar sig främst till myndighetsanställda, medan privatpersoners service sker via kontor.

De fyra är bra kandidater eftersom de ger varierande problemområden och interaktionsmönster. För hackathonets första jämförelsemängd skulle jag prioritera **AF, FK och Skatteverket** (röststyrda ärendebeskrivningar), och lägga till **Migrationsverket** som knappvalsbaserad kontrast. Polis och Kronofogden kan följa när vi väl har en tydlig policy för test av verkliga offentliga nummer.
