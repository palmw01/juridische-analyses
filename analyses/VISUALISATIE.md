# Visueel Overzicht Juridische Analyses

Dit bestand biedt een visuele representatie van de samenhang tussen de geanalyseerde wetsartikelen en de interne logica van de JAS-annotaties.

## 1. De Juridische Kenniskaart (Knowledge Graph)
Deze grafiek toont hoe de verschillende wetten en artikelen in jouw analyses met elkaar verbonden zijn via verwijzingen en hiërarchie.

```mermaid
graph TD
    %% Wetten
    AWB[Algemene wet bestuursrecht]
    IW[Invorderingswet 1990]
    LI[Leidraad Invordering 2008]

    %% Artikelen
    A486[Art. 4:86 Awb<br/><i>Betalingstermijn</i>]
    A492[Art. 4:92 Awb<br/><i>Toerekening</i>]
    
    A7[Art. 7 IW<br/><i>Toerekening betalingen</i>]
    A9[Art. 9 IW<br/><i>Vervaltermijnen</i>]
    
    L91[Art. 9.1 LI]
    L95[Art. 9.5 LI]
    L74[Art. 7.4 LI]

    %% Relaties
    AWB --> A486
    AWB --> A492
    
    IW --> A7
    IW --> A9
    
    LI --> L91
    LI --> L95
    LI --> L74

    %% Verwijzingen (Cross-references)
    A7 -- "Wijk af van" --> A492
    L74 -- "Verduidelijkt" --> A7
    A9 -- "Samenhang met" --> L91
    A9 -- "Samenhang met" --> L95
    
    style IW fill:#f9f,stroke:#333,stroke-width:4px
    style A7 fill:#bbf,stroke:#333,stroke-width:2px
```

## 2. Logische Flow: Art. 7 IW 1990 (JAS-gebaseerd)
Hieronder zie je hoe de JAS-elementen (Voorwaarden, Objecten, Regels) uit je analyse van Artikel 7 een beslisboom vormen.

```mermaid
flowchart LR
    Start([Betaling ontvangen]) --> CondEU{EU Recht<br/>noodzaakt?}
    
    %% Lid 3
    CondEU -- Ja --> Lid3[Volg Ministeriële Regeling]
    
    %% Lid 1
    CondEU -- Nee --> Lid1{Hoofdregel<br/>Art 7 lid 1}
    
    subgraph Toerekening_Volgorde [Strikte Volgorde - Operator: Achtereenvolgens]
        direction TB
        Obj1[1. Kosten]
        Obj2[2. Rente]
        Obj3[3. Belastingaanslag]
        Obj1 --> Obj2 --> Obj3
    end
    
    Lid1 --> Toerekening_Volgorde
    
    %% Lid 2
    Obj3 --> Lid2{Lid 2: Binnen de aanslag?}
    Lid2 -- "Regel: Evenredigheid" --> Var[In te vorderen bedragen<br/>op aanslagbiljet]

    style Toerekening_Volgorde fill:#eee,stroke:#999
    style Lid3 fill:#f66,color:#fff
```

## 3. Innovatie-idee: "Complexity Heatmap"
Als we dit verder trekken, kunnen we per artikel een 'score' berekenen op basis van je JAS-tabellen:
- **Veel Rechtsobjecten?** Hoge informatiedichtheid.
- **Veel Voorwaarden?** Hoge juridische complexiteit.
- **Veel Operators?** Hoge rekenkundige complexiteit.

| Artikel | Info Score | Complexiteit | Status |
| :--- | :---: | :---: | :--- |
| Art. 7 IW | Medium | Medium | ✅ Geannoteerd |
| Art. 9 IW | High | High | 🔄 3 versies |
| Art. 4:86 Awb | Low | Low | ✅ Geannoteerd |

---
*Tip: Gebruik een Markdown-viewer met Mermaid-ondersteuning (zoals VS Code, Obsidian of GitHub) om de grafieken te bekijken.*
