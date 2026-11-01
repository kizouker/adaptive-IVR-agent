# IVR-karta: Region Skåne kundcenter (patientfaktura)

Samtal fredag 30 okt 2026. Ärende: faktura för uteblivet besök, betalas idag, kommer in måndag.
Del av IVR-projektet (Arbetsförmedlingen-agenten / Meta hackathon v44).

## 1. Samtalet som graf

```mermaid
flowchart TD
    start(["Ring Region Skåne"]) --> lang{"Språkval<br/>9 = English"}
    lang --> main1{"Huvudmeny<br/>1 = patientfaktura<br/>2 = tandvårdsstöd"}
    main1 -- "fel val" --> err1["Felaktigt menyval<br/>menyn spelas igen"]
    err1 --> main2{"Huvudmeny igen"}
    main2 -- "fel val igen" --> fallback["Du kopplas nu vidare<br/>FALLBACK-KANT"]
    main1 -- "1" --> pnr
    main2 -- "1" --> pnr
    fallback --> pnr{"Personnummer?<br/>10 siffror + #<br/>eller vänta kvar"}
    pnr --> ident{"Identifiering<br/>1 = BankID<br/>? = Freja"}
    ident -- "1" --> bankid["Starta BankID<br/>i telefonen"]
    bankid --> queue["Kö-meddelande<br/>vi har kö just nu"]
    queue --> cb{"Ring upp mig?<br/>1 = behåll plats<br/>och bli uppringd"}
    cb -- "vänta kvar" --> wait["Väntar<br/>tack för att du väntar"]
    cb -- "1" --> callback["Callback"]
    wait --> human(["Människa: [name removed]<br/>kundcenter"])
    callback --> human
    human --> issue["Ärende: betalt idag<br/>pengarna kommer måndag"]
    issue --> note["Notering till<br/>ekonomiavdelningen<br/>+ kontaktuppgifter"]

    classDef fall fill:#FAEEDA,stroke:#854F0B,color:#633806
    classDef person fill:#E1F5EE,stroke:#0F6E56,color:#085041
    class fallback,err1 fall
    class human person
```

## 2. Hur det kopplas till IVR-agenten

```mermaid
flowchart LR
    rs["Region Skåne-samtalet<br/>30 okt"] --> rec
    af["Arbetsförmedlingen-samtalet<br/>inspelat i okt"] --> rec

    subgraph agent ["Din IVR-agent"]
        rec["record_call"] --> stt["transcribe_audio<br/>Whisper"]
        stt --> parse["parse_prompts<br/>hitta menyval, kö, fallback"]
        parse --> map["build_menu_map<br/>en graf per myndighet"]
        parse --> qw["queue_watch<br/>kö-plats"]
        qw --> alert["iPhone-larm<br/>Swift-app"]
        alert --> you(["Du tar över samtalet"])
    end

    map --> db[("Menykartor<br/>nod = röstmeddelande<br/>kant = knapp eller ord")]

    subgraph hack ["Meta hackathon v44"]
        llama["Llama via Meta API"]
    end
    llama -.-> parse
```

## 3. Vad det här samtalet lär agenten

| Mönster | Region Skåne | Arbetsförmedlingen |
|---|---|---|
| Vägen till en människa | Två fel menyval i rad, sedan "du kopplas nu vidare" | Säga "jag vill ha handläggare", två gånger |
| Identifiering | Personnummer + # (valfritt), BankID eller Freja | BankID med personnummer |
| Kö | "Vi har kö", ingen kö-plats sägs | Kö-plats sägs och upprepas |
| Ring upp mig | Finns (tryck 1) | Saknas (det är det agenten ska göra) |

Slutsatser:

1. **Fallback-kanter** ska vara en egen typ av kant i grafen: "vad händer om man gör fel eller inget". Båda systemen har en sådan väg till en människa.
2. **Samma schema för alla myndigheter**: nodtyper = språkval, meny, identifiering, kö, callback, människa. Då kan agenten jämföra system.
3. **Pitch till hackathon**: Region Skåne har redan "ring upp mig". Agenten ger samma sak hos myndigheter som saknar den, och vet kö-platsen.
