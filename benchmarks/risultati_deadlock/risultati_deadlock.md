# Risultati test deadlock e regola di precedenza (4 droni)

Regola di precedenza testata (senza riaddestramento): in caso di contesa della stessa cella libera, passa il drone con **minore distanza Manhattan dall'hangar** (a parità di distanza, indice minore `D0 > D1 > D2 > D3`).

## Scenari con posizionamento specifico (seed modello: 42)

### [MAPPO - seed 42 - SENZA PRECEDENZA] Caso 1a - Contesa della stessa casella ai lati dell'hangar (2 droni)
Hangar in (4,8). I droni D0 e D2 sono gia arrivati, mentre D1 in (5,7) e D3 in (4,6) cercano entrambi di passare per la casella (4,7) sopra l'hangar.
- Hangar: `(4, 8)` | Montagne: `[(1, 1), (8, 1), (1, 4), (8, 4)]` | Droni: `[(4, 8), (5, 7), (4, 8), (4, 6)]`

```text
Step   1: pos=[(4, 8), (5, 7), (4, 8), (4, 6)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(4, 8), (5, 8), (4, 8), (4, 7)] (droni mossi: [1, 3])
Step   2: pos=[(4, 8), (5, 8), (4, 8), (4, 7)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(4, 8), (5, 9), (4, 8), (4, 8)] (droni mossi: [1, 3])
Step   3: pos=[(4, 8), (5, 9), (4, 8), (4, 8)] | azioni=[D0:arrivato, D1:Su, D2:arrivato, D3:arrivato]
          -> nuove pos=[(4, 8), (5, 8), (4, 8), (4, 8)] (droni mossi: [1])
Step   4: pos=[(4, 8), (5, 8), (4, 8), (4, 8)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:arrivato]
          -> nuove pos=[(4, 8), (5, 9), (4, 8), (4, 8)] (droni mossi: [1])
Step   5: pos=[(4, 8), (5, 9), (4, 8), (4, 8)] | azioni=[D0:arrivato, D1:Su, D2:arrivato, D3:arrivato]
          -> nuove pos=[(4, 8), (5, 8), (4, 8), (4, 8)] (droni mossi: [1])
Step   6: pos=[(4, 8), (5, 8), (4, 8), (4, 8)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:arrivato]
          -> nuove pos=[(4, 8), (5, 9), (4, 8), (4, 8)] (droni mossi: [1])
Step   7: pos=[(4, 8), (5, 9), (4, 8), (4, 8)] | azioni=[D0:arrivato, D1:Su, D2:arrivato, D3:arrivato]
          -> nuove pos=[(4, 8), (5, 8), (4, 8), (4, 8)] (droni mossi: [1])
Step   8: pos=[(4, 8), (5, 8), (4, 8), (4, 8)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:arrivato]
          -> nuove pos=[(4, 8), (5, 9), (4, 8), (4, 8)] (droni mossi: [1])
  ... (dal passo 9 al 97 si ripete lo stesso comportamento) ...
Step  98: pos=[(4, 8), (5, 8), (4, 8), (4, 8)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:arrivato]
          -> nuove pos=[(4, 8), (5, 9), (4, 8), (4, 8)] (droni mossi: [1])
Step  99: pos=[(4, 8), (5, 9), (4, 8), (4, 8)] | azioni=[D0:arrivato, D1:Su, D2:arrivato, D3:arrivato]
          -> nuove pos=[(4, 8), (5, 8), (4, 8), (4, 8)] (droni mossi: [1])
Step 100: pos=[(4, 8), (5, 8), (4, 8), (4, 8)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:arrivato]
          -> nuove pos=[(4, 8), (5, 9), (4, 8), (4, 8)] (droni mossi: [1])
```

- Esito: fallimento per timeout a 100 step (reward: -1.0, droni arrivati: 3/4, precedenze attivate: 0)
- Comportamento: i droni continuano a muoversi senza progredire
  - Drone D1: si muove avanti e indietro tra le celle [(5, 9), (5, 8)]

### [MAPPO - seed 42 - CON PRECEDENZA] Caso 1a - Contesa della stessa casella ai lati dell'hangar (2 droni)
Hangar in (4,8). I droni D0 e D2 sono gia arrivati, mentre D1 in (5,7) e D3 in (4,6) cercano entrambi di passare per la casella (4,7) sopra l'hangar.
- Hangar: `(4, 8)` | Montagne: `[(1, 1), (8, 1), (1, 4), (8, 4)]` | Droni: `[(4, 8), (5, 7), (4, 8), (4, 6)]`

```text
Step   1: pos=[(4, 8), (5, 7), (4, 8), (4, 6)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(4, 8), (5, 8), (4, 8), (4, 7)] (droni mossi: [1, 3])
Step   2: pos=[(4, 8), (5, 8), (4, 8), (4, 7)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(4, 8), (5, 9), (4, 8), (4, 8)] (droni mossi: [1, 3])
Step   3: pos=[(4, 8), (5, 9), (4, 8), (4, 8)] | azioni=[D0:arrivato, D1:Su, D2:arrivato, D3:arrivato]
          -> nuove pos=[(4, 8), (5, 8), (4, 8), (4, 8)] (droni mossi: [1])
Step   4: pos=[(4, 8), (5, 8), (4, 8), (4, 8)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:arrivato]
          -> nuove pos=[(4, 8), (5, 9), (4, 8), (4, 8)] (droni mossi: [1])
Step   5: pos=[(4, 8), (5, 9), (4, 8), (4, 8)] | azioni=[D0:arrivato, D1:Su, D2:arrivato, D3:arrivato]
          -> nuove pos=[(4, 8), (5, 8), (4, 8), (4, 8)] (droni mossi: [1])
Step   6: pos=[(4, 8), (5, 8), (4, 8), (4, 8)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:arrivato]
          -> nuove pos=[(4, 8), (5, 9), (4, 8), (4, 8)] (droni mossi: [1])
Step   7: pos=[(4, 8), (5, 9), (4, 8), (4, 8)] | azioni=[D0:arrivato, D1:Su, D2:arrivato, D3:arrivato]
          -> nuove pos=[(4, 8), (5, 8), (4, 8), (4, 8)] (droni mossi: [1])
Step   8: pos=[(4, 8), (5, 8), (4, 8), (4, 8)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:arrivato]
          -> nuove pos=[(4, 8), (5, 9), (4, 8), (4, 8)] (droni mossi: [1])
  ... (dal passo 9 al 97 si ripete lo stesso comportamento) ...
Step  98: pos=[(4, 8), (5, 8), (4, 8), (4, 8)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:arrivato]
          -> nuove pos=[(4, 8), (5, 9), (4, 8), (4, 8)] (droni mossi: [1])
Step  99: pos=[(4, 8), (5, 9), (4, 8), (4, 8)] | azioni=[D0:arrivato, D1:Su, D2:arrivato, D3:arrivato]
          -> nuove pos=[(4, 8), (5, 8), (4, 8), (4, 8)] (droni mossi: [1])
Step 100: pos=[(4, 8), (5, 8), (4, 8), (4, 8)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:arrivato]
          -> nuove pos=[(4, 8), (5, 9), (4, 8), (4, 8)] (droni mossi: [1])
```

- Esito: fallimento per timeout a 100 step (reward: -1.0, droni arrivati: 3/4, precedenze attivate: 0)
- Comportamento: i droni continuano a muoversi senza progredire
  - Drone D1: si muove avanti e indietro tra le celle [(5, 9), (5, 8)]

### [MAPPO - seed 42 - SENZA PRECEDENZA] Caso 1b - Contesa ai lati dell'hangar con 4 droni
Hangar in (5,5) con montagne sopra (5,4) e sotto (5,6). D0(3,5) e D1(4,4) puntano al lato sinistro (4,5), mentre D2(7,5) e D3(6,6) puntano al lato destro (6,5).
- Hangar: `(5, 5)` | Montagne: `[(5, 4), (5, 6), (1, 1), (8, 8)]` | Droni: `[(3, 5), (4, 4), (7, 5), (6, 6)]`

```text
Step   1: pos=[(3, 5), (4, 4), (7, 5), (6, 6)] | azioni=[D0:Giu, D1:Giu, D2:Sinistra, D3:Sinistra]
          -> nuove pos=[(3, 6), (4, 5), (6, 5), (6, 6)] (D3 da (6, 6) colpisce la montagna in (5, 6))
Step   2: pos=[(3, 6), (4, 5), (6, 5), (6, 6)] | azioni=[D0:Destra, D1:Giu, D2:Sinistra, D3:Su]
          -> nuove pos=[(3, 6), (4, 5), (5, 5), (6, 5)] (scontro tra D0(3, 6) e D1(4, 5) sulla cella (4, 6))
Step   3: pos=[(3, 6), (4, 5), (5, 5), (6, 5)] | azioni=[D0:Destra, D1:Destra, D2:arrivato, D3:Sinistra]
          -> nuove pos=[(4, 6), (5, 5), (5, 5), (5, 5)] (droni mossi: [0, 1, 3])
Step   4: pos=[(4, 6), (5, 5), (5, 5), (5, 5)] | azioni=[D0:Su, D1:arrivato, D2:arrivato, D3:arrivato]
          -> nuove pos=[(4, 5), (5, 5), (5, 5), (5, 5)] (droni mossi: [0])
Step   5: pos=[(4, 5), (5, 5), (5, 5), (5, 5)] | azioni=[D0:Su, D1:arrivato, D2:arrivato, D3:arrivato]
          -> nuove pos=[(4, 4), (5, 5), (5, 5), (5, 5)] (droni mossi: [0])
Step   6: pos=[(4, 4), (5, 5), (5, 5), (5, 5)] | azioni=[D0:Giu, D1:arrivato, D2:arrivato, D3:arrivato]
          -> nuove pos=[(4, 5), (5, 5), (5, 5), (5, 5)] (droni mossi: [0])
Step   7: pos=[(4, 5), (5, 5), (5, 5), (5, 5)] | azioni=[D0:Su, D1:arrivato, D2:arrivato, D3:arrivato]
          -> nuove pos=[(4, 4), (5, 5), (5, 5), (5, 5)] (droni mossi: [0])
Step   8: pos=[(4, 4), (5, 5), (5, 5), (5, 5)] | azioni=[D0:Giu, D1:arrivato, D2:arrivato, D3:arrivato]
          -> nuove pos=[(4, 5), (5, 5), (5, 5), (5, 5)] (droni mossi: [0])
  ... (dal passo 9 al 97 si ripete lo stesso comportamento) ...
Step  98: pos=[(4, 4), (5, 5), (5, 5), (5, 5)] | azioni=[D0:Giu, D1:arrivato, D2:arrivato, D3:arrivato]
          -> nuove pos=[(4, 5), (5, 5), (5, 5), (5, 5)] (droni mossi: [0])
Step  99: pos=[(4, 5), (5, 5), (5, 5), (5, 5)] | azioni=[D0:Su, D1:arrivato, D2:arrivato, D3:arrivato]
          -> nuove pos=[(4, 4), (5, 5), (5, 5), (5, 5)] (droni mossi: [0])
Step 100: pos=[(4, 4), (5, 5), (5, 5), (5, 5)] | azioni=[D0:Giu, D1:arrivato, D2:arrivato, D3:arrivato]
          -> nuove pos=[(4, 5), (5, 5), (5, 5), (5, 5)] (droni mossi: [0])
```

- Esito: fallimento per timeout a 100 step (reward: 165.0, droni arrivati: 3/4, precedenze attivate: 0)
- Comportamento: i droni continuano a muoversi senza progredire
  - Drone D0: si muove avanti e indietro tra le celle [(4, 5), (4, 4)]

### [MAPPO - seed 42 - CON PRECEDENZA] Caso 1b - Contesa ai lati dell'hangar con 4 droni
Hangar in (5,5) con montagne sopra (5,4) e sotto (5,6). D0(3,5) e D1(4,4) puntano al lato sinistro (4,5), mentre D2(7,5) e D3(6,6) puntano al lato destro (6,5).
- Hangar: `(5, 5)` | Montagne: `[(5, 4), (5, 6), (1, 1), (8, 8)]` | Droni: `[(3, 5), (4, 4), (7, 5), (6, 6)]`

```text
Step   1: pos=[(3, 5), (4, 4), (7, 5), (6, 6)] | azioni=[D0:Giu, D1:Giu, D2:Sinistra, D3:Sinistra]
          -> nuove pos=[(3, 6), (4, 5), (6, 5), (6, 6)] (D3 da (6, 6) colpisce la montagna in (5, 6))
Step   2: pos=[(3, 6), (4, 5), (6, 5), (6, 6)] | azioni=[D0:Destra, D1:Giu, D2:Sinistra, D3:Su]
          -> nuove pos=[(4, 6), (4, 5), (5, 5), (6, 5)] (precedenza su (4, 6): passa D0(3, 6) (dist=3), attende D1(4, 5) (dist=1))
Step   3: pos=[(4, 6), (4, 5), (5, 5), (6, 5)] | azioni=[D0:Destra, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(4, 6), (4, 5), (5, 5), (6, 6)] (scontro tra D0(4, 6) e D1(4, 5) sulla cella (4, 6) | D0 da (4, 6) colpisce la montagna in (5, 6))
Step   4: pos=[(4, 6), (4, 5), (5, 5), (6, 6)] | azioni=[D0:Destra, D1:Giu, D2:arrivato, D3:Su]
          -> nuove pos=[(4, 6), (4, 5), (5, 5), (6, 5)] (scontro tra D0(4, 6) e D1(4, 5) sulla cella (4, 6) | D0 da (4, 6) colpisce la montagna in (5, 6))
Step   5: pos=[(4, 6), (4, 5), (5, 5), (6, 5)] | azioni=[D0:Destra, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(4, 6), (4, 5), (5, 5), (6, 6)] (scontro tra D0(4, 6) e D1(4, 5) sulla cella (4, 6) | D0 da (4, 6) colpisce la montagna in (5, 6))
Step   6: pos=[(4, 6), (4, 5), (5, 5), (6, 6)] | azioni=[D0:Destra, D1:Giu, D2:arrivato, D3:Su]
          -> nuove pos=[(4, 6), (4, 5), (5, 5), (6, 5)] (scontro tra D0(4, 6) e D1(4, 5) sulla cella (4, 6) | D0 da (4, 6) colpisce la montagna in (5, 6))
Step   7: pos=[(4, 6), (4, 5), (5, 5), (6, 5)] | azioni=[D0:Destra, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(4, 6), (4, 5), (5, 5), (6, 6)] (scontro tra D0(4, 6) e D1(4, 5) sulla cella (4, 6) | D0 da (4, 6) colpisce la montagna in (5, 6))
Step   8: pos=[(4, 6), (4, 5), (5, 5), (6, 6)] | azioni=[D0:Destra, D1:Giu, D2:arrivato, D3:Su]
          -> nuove pos=[(4, 6), (4, 5), (5, 5), (6, 5)] (scontro tra D0(4, 6) e D1(4, 5) sulla cella (4, 6) | D0 da (4, 6) colpisce la montagna in (5, 6))
  ... (dal passo 9 al 97 si ripete lo stesso comportamento) ...
Step  98: pos=[(4, 6), (4, 5), (5, 5), (6, 6)] | azioni=[D0:Destra, D1:Giu, D2:arrivato, D3:Su]
          -> nuove pos=[(4, 6), (4, 5), (5, 5), (6, 5)] (scontro tra D0(4, 6) e D1(4, 5) sulla cella (4, 6) | D0 da (4, 6) colpisce la montagna in (5, 6))
Step  99: pos=[(4, 6), (4, 5), (5, 5), (6, 5)] | azioni=[D0:Destra, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(4, 6), (4, 5), (5, 5), (6, 6)] (scontro tra D0(4, 6) e D1(4, 5) sulla cella (4, 6) | D0 da (4, 6) colpisce la montagna in (5, 6))
Step 100: pos=[(4, 6), (4, 5), (5, 5), (6, 6)] | azioni=[D0:Destra, D1:Giu, D2:arrivato, D3:Su]
          -> nuove pos=[(4, 6), (4, 5), (5, 5), (6, 5)] (scontro tra D0(4, 6) e D1(4, 5) sulla cella (4, 6) | D0 da (4, 6) colpisce la montagna in (5, 6))
```

- Esito: fallimento per timeout a 100 step (reward: -3151.0, droni arrivati: 1/4, precedenze attivate: 1)
- Comportamento: i droni continuano a muoversi senza progredire
  - Drone D0: resta fermo nella cella (4, 6)
  - Drone D1: resta fermo nella cella (4, 5)
  - Drone D3: si muove avanti e indietro tra le celle [(6, 5), (6, 6)]

### [MAPPO - seed 42 - SENZA PRECEDENZA] Caso 2a - Montagne a 1 cella dal bordo sinistro
Montagne in (1,5), (2,5), (3,5), (4,5) che lasciano solo la cella (0,5) libera sul bordo sinistro. Hangar in (0,7) e droni in (0,4), (1,4), (0,3) e (2,4) che devono passare da (0,5).
- Hangar: `(0, 7)` | Montagne: `[(1, 5), (2, 5), (3, 5), (4, 5)]` | Droni: `[(0, 4), (1, 4), (0, 3), (2, 4)]`

```text
Step   1: pos=[(0, 4), (1, 4), (0, 3), (2, 4)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 5), (1, 4), (0, 4), (2, 4)] (D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5))
Step   2: pos=[(0, 5), (1, 4), (0, 4), (2, 4)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 6), (1, 4), (0, 5), (2, 4)] (D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5))
Step   3: pos=[(0, 6), (1, 4), (0, 5), (2, 4)] | azioni=[D0:Sinistra, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 6), (1, 4), (0, 5), (2, 4)] (scontro tra D0(0, 6) e D2(0, 5) sulla cella (0, 6) a lato dell'hangar | D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5) | D0 da (0, 6) tocca il bordo mappa)
Step   4: pos=[(0, 6), (1, 4), (0, 5), (2, 4)] | azioni=[D0:Sinistra, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 6), (1, 4), (0, 5), (2, 4)] (scontro tra D0(0, 6) e D2(0, 5) sulla cella (0, 6) a lato dell'hangar | D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5) | D0 da (0, 6) tocca il bordo mappa)
Step   5: pos=[(0, 6), (1, 4), (0, 5), (2, 4)] | azioni=[D0:Sinistra, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 6), (1, 4), (0, 5), (2, 4)] (scontro tra D0(0, 6) e D2(0, 5) sulla cella (0, 6) a lato dell'hangar | D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5) | D0 da (0, 6) tocca il bordo mappa)
Step   6: pos=[(0, 6), (1, 4), (0, 5), (2, 4)] | azioni=[D0:Sinistra, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 6), (1, 4), (0, 5), (2, 4)] (scontro tra D0(0, 6) e D2(0, 5) sulla cella (0, 6) a lato dell'hangar | D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5) | D0 da (0, 6) tocca il bordo mappa)
Step   7: pos=[(0, 6), (1, 4), (0, 5), (2, 4)] | azioni=[D0:Sinistra, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 6), (1, 4), (0, 5), (2, 4)] (scontro tra D0(0, 6) e D2(0, 5) sulla cella (0, 6) a lato dell'hangar | D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5) | D0 da (0, 6) tocca il bordo mappa)
Step   8: pos=[(0, 6), (1, 4), (0, 5), (2, 4)] | azioni=[D0:Sinistra, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 6), (1, 4), (0, 5), (2, 4)] (scontro tra D0(0, 6) e D2(0, 5) sulla cella (0, 6) a lato dell'hangar | D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5) | D0 da (0, 6) tocca il bordo mappa)
  ... (dal passo 9 al 97 si ripete lo stesso comportamento) ...
Step  98: pos=[(0, 6), (1, 4), (0, 5), (2, 4)] | azioni=[D0:Sinistra, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 6), (1, 4), (0, 5), (2, 4)] (scontro tra D0(0, 6) e D2(0, 5) sulla cella (0, 6) a lato dell'hangar | D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5) | D0 da (0, 6) tocca il bordo mappa)
Step  99: pos=[(0, 6), (1, 4), (0, 5), (2, 4)] | azioni=[D0:Sinistra, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 6), (1, 4), (0, 5), (2, 4)] (scontro tra D0(0, 6) e D2(0, 5) sulla cella (0, 6) a lato dell'hangar | D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5) | D0 da (0, 6) tocca il bordo mappa)
Step 100: pos=[(0, 6), (1, 4), (0, 5), (2, 4)] | azioni=[D0:Sinistra, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 6), (1, 4), (0, 5), (2, 4)] (scontro tra D0(0, 6) e D2(0, 5) sulla cella (0, 6) a lato dell'hangar | D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5) | D0 da (0, 6) tocca il bordo mappa)
```

- Esito: fallimento per timeout a 100 step (reward: -5340.0, droni arrivati: 0/4, precedenze attivate: 0)
- Comportamento: i droni rimangono effettivamente bloccati
  - Drone D0: resta fermo nella cella (0, 6)
  - Drone D1: resta fermo nella cella (1, 4)
  - Drone D2: resta fermo nella cella (0, 5)
  - Drone D3: resta fermo nella cella (2, 4)

### [MAPPO - seed 42 - CON PRECEDENZA] Caso 2a - Montagne a 1 cella dal bordo sinistro
Montagne in (1,5), (2,5), (3,5), (4,5) che lasciano solo la cella (0,5) libera sul bordo sinistro. Hangar in (0,7) e droni in (0,4), (1,4), (0,3) e (2,4) che devono passare da (0,5).
- Hangar: `(0, 7)` | Montagne: `[(1, 5), (2, 5), (3, 5), (4, 5)]` | Droni: `[(0, 4), (1, 4), (0, 3), (2, 4)]`

```text
Step   1: pos=[(0, 4), (1, 4), (0, 3), (2, 4)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 5), (1, 4), (0, 4), (2, 4)] (D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5))
Step   2: pos=[(0, 5), (1, 4), (0, 4), (2, 4)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 6), (1, 4), (0, 5), (2, 4)] (D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5))
Step   3: pos=[(0, 6), (1, 4), (0, 5), (2, 4)] | azioni=[D0:Sinistra, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 6), (1, 4), (0, 5), (2, 4)] (scontro tra D0(0, 6) e D2(0, 5) sulla cella (0, 6) a lato dell'hangar | D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5) | D0 da (0, 6) tocca il bordo mappa)
Step   4: pos=[(0, 6), (1, 4), (0, 5), (2, 4)] | azioni=[D0:Sinistra, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 6), (1, 4), (0, 5), (2, 4)] (scontro tra D0(0, 6) e D2(0, 5) sulla cella (0, 6) a lato dell'hangar | D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5) | D0 da (0, 6) tocca il bordo mappa)
Step   5: pos=[(0, 6), (1, 4), (0, 5), (2, 4)] | azioni=[D0:Sinistra, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 6), (1, 4), (0, 5), (2, 4)] (scontro tra D0(0, 6) e D2(0, 5) sulla cella (0, 6) a lato dell'hangar | D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5) | D0 da (0, 6) tocca il bordo mappa)
Step   6: pos=[(0, 6), (1, 4), (0, 5), (2, 4)] | azioni=[D0:Sinistra, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 6), (1, 4), (0, 5), (2, 4)] (scontro tra D0(0, 6) e D2(0, 5) sulla cella (0, 6) a lato dell'hangar | D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5) | D0 da (0, 6) tocca il bordo mappa)
Step   7: pos=[(0, 6), (1, 4), (0, 5), (2, 4)] | azioni=[D0:Sinistra, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 6), (1, 4), (0, 5), (2, 4)] (scontro tra D0(0, 6) e D2(0, 5) sulla cella (0, 6) a lato dell'hangar | D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5) | D0 da (0, 6) tocca il bordo mappa)
Step   8: pos=[(0, 6), (1, 4), (0, 5), (2, 4)] | azioni=[D0:Sinistra, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 6), (1, 4), (0, 5), (2, 4)] (scontro tra D0(0, 6) e D2(0, 5) sulla cella (0, 6) a lato dell'hangar | D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5) | D0 da (0, 6) tocca il bordo mappa)
  ... (dal passo 9 al 97 si ripete lo stesso comportamento) ...
Step  98: pos=[(0, 6), (1, 4), (0, 5), (2, 4)] | azioni=[D0:Sinistra, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 6), (1, 4), (0, 5), (2, 4)] (scontro tra D0(0, 6) e D2(0, 5) sulla cella (0, 6) a lato dell'hangar | D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5) | D0 da (0, 6) tocca il bordo mappa)
Step  99: pos=[(0, 6), (1, 4), (0, 5), (2, 4)] | azioni=[D0:Sinistra, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 6), (1, 4), (0, 5), (2, 4)] (scontro tra D0(0, 6) e D2(0, 5) sulla cella (0, 6) a lato dell'hangar | D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5) | D0 da (0, 6) tocca il bordo mappa)
Step 100: pos=[(0, 6), (1, 4), (0, 5), (2, 4)] | azioni=[D0:Sinistra, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 6), (1, 4), (0, 5), (2, 4)] (scontro tra D0(0, 6) e D2(0, 5) sulla cella (0, 6) a lato dell'hangar | D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5) | D0 da (0, 6) tocca il bordo mappa)
```

- Esito: fallimento per timeout a 100 step (reward: -5340.0, droni arrivati: 0/4, precedenze attivate: 0)
- Comportamento: i droni rimangono effettivamente bloccati
  - Drone D0: resta fermo nella cella (0, 6)
  - Drone D1: resta fermo nella cella (1, 4)
  - Drone D2: resta fermo nella cella (0, 5)
  - Drone D3: resta fermo nella cella (2, 4)

### [MAPPO - seed 42 - SENZA PRECEDENZA] Caso 2b - Montagne a 1 cella dal bordo superiore
Montagne in (5,1), (5,2), (5,3), (5,4) che lasciano solo la cella (5,0) libera sul bordo in alto. Hangar in (7,0) e droni in (4,0), (4,1), (3,0), (4,2) che devono passare da (5,0).
- Hangar: `(7, 0)` | Montagne: `[(5, 1), (5, 2), (5, 3), (5, 4)]` | Droni: `[(4, 0), (4, 1), (3, 0), (4, 2)]`

```text
Step   1: pos=[(4, 0), (4, 1), (3, 0), (4, 2)] | azioni=[D0:Fermo, D1:Fermo, D2:Fermo, D3:Fermo]
          -> nuove pos=[(4, 0), (4, 1), (3, 0), (4, 2)] (droni fermi: ['D0', 'D1', 'D2', 'D3'])
Step   2: pos=[(4, 0), (4, 1), (3, 0), (4, 2)] | azioni=[D0:Fermo, D1:Fermo, D2:Fermo, D3:Fermo]
          -> nuove pos=[(4, 0), (4, 1), (3, 0), (4, 2)] (droni fermi: ['D0', 'D1', 'D2', 'D3'])
Step   3: pos=[(4, 0), (4, 1), (3, 0), (4, 2)] | azioni=[D0:Fermo, D1:Fermo, D2:Fermo, D3:Fermo]
          -> nuove pos=[(4, 0), (4, 1), (3, 0), (4, 2)] (droni fermi: ['D0', 'D1', 'D2', 'D3'])
Step   4: pos=[(4, 0), (4, 1), (3, 0), (4, 2)] | azioni=[D0:Fermo, D1:Fermo, D2:Fermo, D3:Fermo]
          -> nuove pos=[(4, 0), (4, 1), (3, 0), (4, 2)] (droni fermi: ['D0', 'D1', 'D2', 'D3'])
Step   5: pos=[(4, 0), (4, 1), (3, 0), (4, 2)] | azioni=[D0:Fermo, D1:Fermo, D2:Fermo, D3:Fermo]
          -> nuove pos=[(4, 0), (4, 1), (3, 0), (4, 2)] (droni fermi: ['D0', 'D1', 'D2', 'D3'])
Step   6: pos=[(4, 0), (4, 1), (3, 0), (4, 2)] | azioni=[D0:Fermo, D1:Fermo, D2:Fermo, D3:Fermo]
          -> nuove pos=[(4, 0), (4, 1), (3, 0), (4, 2)] (droni fermi: ['D0', 'D1', 'D2', 'D3'])
Step   7: pos=[(4, 0), (4, 1), (3, 0), (4, 2)] | azioni=[D0:Fermo, D1:Fermo, D2:Fermo, D3:Fermo]
          -> nuove pos=[(4, 0), (4, 1), (3, 0), (4, 2)] (droni fermi: ['D0', 'D1', 'D2', 'D3'])
Step   8: pos=[(4, 0), (4, 1), (3, 0), (4, 2)] | azioni=[D0:Fermo, D1:Fermo, D2:Fermo, D3:Fermo]
          -> nuove pos=[(4, 0), (4, 1), (3, 0), (4, 2)] (droni fermi: ['D0', 'D1', 'D2', 'D3'])
  ... (dal passo 9 al 97 si ripete lo stesso comportamento) ...
Step  98: pos=[(4, 0), (4, 1), (3, 0), (4, 2)] | azioni=[D0:Fermo, D1:Fermo, D2:Fermo, D3:Fermo]
          -> nuove pos=[(4, 0), (4, 1), (3, 0), (4, 2)] (droni fermi: ['D0', 'D1', 'D2', 'D3'])
Step  99: pos=[(4, 0), (4, 1), (3, 0), (4, 2)] | azioni=[D0:Fermo, D1:Fermo, D2:Fermo, D3:Fermo]
          -> nuove pos=[(4, 0), (4, 1), (3, 0), (4, 2)] (droni fermi: ['D0', 'D1', 'D2', 'D3'])
Step 100: pos=[(4, 0), (4, 1), (3, 0), (4, 2)] | azioni=[D0:Fermo, D1:Fermo, D2:Fermo, D3:Fermo]
          -> nuove pos=[(4, 0), (4, 1), (3, 0), (4, 2)] (droni fermi: ['D0', 'D1', 'D2', 'D3'])
```

- Esito: fallimento per timeout a 100 step (reward: -400.0, droni arrivati: 0/4, precedenze attivate: 0)
- Comportamento: i droni rimangono effettivamente bloccati
  - Drone D0: resta fermo nella cella (4, 0)
  - Drone D1: resta fermo nella cella (4, 1)
  - Drone D2: resta fermo nella cella (3, 0)
  - Drone D3: resta fermo nella cella (4, 2)

### [MAPPO - seed 42 - CON PRECEDENZA] Caso 2b - Montagne a 1 cella dal bordo superiore
Montagne in (5,1), (5,2), (5,3), (5,4) che lasciano solo la cella (5,0) libera sul bordo in alto. Hangar in (7,0) e droni in (4,0), (4,1), (3,0), (4,2) che devono passare da (5,0).
- Hangar: `(7, 0)` | Montagne: `[(5, 1), (5, 2), (5, 3), (5, 4)]` | Droni: `[(4, 0), (4, 1), (3, 0), (4, 2)]`

```text
Step   1: pos=[(4, 0), (4, 1), (3, 0), (4, 2)] | azioni=[D0:Fermo, D1:Fermo, D2:Fermo, D3:Fermo]
          -> nuove pos=[(4, 0), (4, 1), (3, 0), (4, 2)] (droni fermi: ['D0', 'D1', 'D2', 'D3'])
Step   2: pos=[(4, 0), (4, 1), (3, 0), (4, 2)] | azioni=[D0:Fermo, D1:Fermo, D2:Fermo, D3:Fermo]
          -> nuove pos=[(4, 0), (4, 1), (3, 0), (4, 2)] (droni fermi: ['D0', 'D1', 'D2', 'D3'])
Step   3: pos=[(4, 0), (4, 1), (3, 0), (4, 2)] | azioni=[D0:Fermo, D1:Fermo, D2:Fermo, D3:Fermo]
          -> nuove pos=[(4, 0), (4, 1), (3, 0), (4, 2)] (droni fermi: ['D0', 'D1', 'D2', 'D3'])
Step   4: pos=[(4, 0), (4, 1), (3, 0), (4, 2)] | azioni=[D0:Fermo, D1:Fermo, D2:Fermo, D3:Fermo]
          -> nuove pos=[(4, 0), (4, 1), (3, 0), (4, 2)] (droni fermi: ['D0', 'D1', 'D2', 'D3'])
Step   5: pos=[(4, 0), (4, 1), (3, 0), (4, 2)] | azioni=[D0:Fermo, D1:Fermo, D2:Fermo, D3:Fermo]
          -> nuove pos=[(4, 0), (4, 1), (3, 0), (4, 2)] (droni fermi: ['D0', 'D1', 'D2', 'D3'])
Step   6: pos=[(4, 0), (4, 1), (3, 0), (4, 2)] | azioni=[D0:Fermo, D1:Fermo, D2:Fermo, D3:Fermo]
          -> nuove pos=[(4, 0), (4, 1), (3, 0), (4, 2)] (droni fermi: ['D0', 'D1', 'D2', 'D3'])
Step   7: pos=[(4, 0), (4, 1), (3, 0), (4, 2)] | azioni=[D0:Fermo, D1:Fermo, D2:Fermo, D3:Fermo]
          -> nuove pos=[(4, 0), (4, 1), (3, 0), (4, 2)] (droni fermi: ['D0', 'D1', 'D2', 'D3'])
Step   8: pos=[(4, 0), (4, 1), (3, 0), (4, 2)] | azioni=[D0:Fermo, D1:Fermo, D2:Fermo, D3:Fermo]
          -> nuove pos=[(4, 0), (4, 1), (3, 0), (4, 2)] (droni fermi: ['D0', 'D1', 'D2', 'D3'])
  ... (dal passo 9 al 97 si ripete lo stesso comportamento) ...
Step  98: pos=[(4, 0), (4, 1), (3, 0), (4, 2)] | azioni=[D0:Fermo, D1:Fermo, D2:Fermo, D3:Fermo]
          -> nuove pos=[(4, 0), (4, 1), (3, 0), (4, 2)] (droni fermi: ['D0', 'D1', 'D2', 'D3'])
Step  99: pos=[(4, 0), (4, 1), (3, 0), (4, 2)] | azioni=[D0:Fermo, D1:Fermo, D2:Fermo, D3:Fermo]
          -> nuove pos=[(4, 0), (4, 1), (3, 0), (4, 2)] (droni fermi: ['D0', 'D1', 'D2', 'D3'])
Step 100: pos=[(4, 0), (4, 1), (3, 0), (4, 2)] | azioni=[D0:Fermo, D1:Fermo, D2:Fermo, D3:Fermo]
          -> nuove pos=[(4, 0), (4, 1), (3, 0), (4, 2)] (droni fermi: ['D0', 'D1', 'D2', 'D3'])
```

- Esito: fallimento per timeout a 100 step (reward: -400.0, droni arrivati: 0/4, precedenze attivate: 0)
- Comportamento: i droni rimangono effettivamente bloccati
  - Drone D0: resta fermo nella cella (4, 0)
  - Drone D1: resta fermo nella cella (4, 1)
  - Drone D2: resta fermo nella cella (3, 0)
  - Drone D3: resta fermo nella cella (4, 2)

### [MAPPO - seed 42 - SENZA PRECEDENZA] Caso 2c - Passaggio di 1 cella lungo il bordo destro
Montagne in (8,5), (8,6), (8,7), (7,7) che lasciano un passaggio di 1 cella sul bordo destro per arrivare all'hangar in (9,8). Droni in partenza da (9,4), (8,4), (9,3), (7,4).
- Hangar: `(9, 8)` | Montagne: `[(8, 5), (8, 6), (8, 7), (7, 7)]` | Droni: `[(9, 4), (8, 4), (9, 3), (7, 4)]`

```text
Step   1: pos=[(9, 4), (8, 4), (9, 3), (7, 4)] | azioni=[D0:Giu, D1:Fermo, D2:Giu, D3:Fermo]
          -> nuove pos=[(9, 5), (8, 4), (9, 4), (7, 4)] (droni fermi: ['D1', 'D3'])
Step   2: pos=[(9, 5), (8, 4), (9, 4), (7, 4)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(9, 6), (8, 4), (9, 5), (7, 5)] (D1 da (8, 4) colpisce la montagna in (8, 5))
Step   3: pos=[(9, 6), (8, 4), (9, 5), (7, 5)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(9, 7), (8, 4), (9, 6), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5))
Step   4: pos=[(9, 7), (8, 4), (9, 6), (7, 6)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 7), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
Step   5: pos=[(9, 8), (8, 4), (9, 7), (7, 6)] | azioni=[D0:arrivato, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 8), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
Step   6: pos=[(9, 8), (8, 4), (9, 8), (7, 6)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 8), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
Step   7: pos=[(9, 8), (8, 4), (9, 8), (7, 6)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 8), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
Step   8: pos=[(9, 8), (8, 4), (9, 8), (7, 6)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 8), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
  ... (dal passo 9 al 97 si ripete lo stesso comportamento) ...
Step  98: pos=[(9, 8), (8, 4), (9, 8), (7, 6)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 8), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
Step  99: pos=[(9, 8), (8, 4), (9, 8), (7, 6)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 8), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
Step 100: pos=[(9, 8), (8, 4), (9, 8), (7, 6)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 8), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
```

- Esito: fallimento per timeout a 100 step (reward: -1967.0, droni arrivati: 2/4, precedenze attivate: 0)
- Comportamento: i droni rimangono effettivamente bloccati
  - Drone D1: resta fermo nella cella (8, 4)
  - Drone D3: resta fermo nella cella (7, 6)

### [MAPPO - seed 42 - CON PRECEDENZA] Caso 2c - Passaggio di 1 cella lungo il bordo destro
Montagne in (8,5), (8,6), (8,7), (7,7) che lasciano un passaggio di 1 cella sul bordo destro per arrivare all'hangar in (9,8). Droni in partenza da (9,4), (8,4), (9,3), (7,4).
- Hangar: `(9, 8)` | Montagne: `[(8, 5), (8, 6), (8, 7), (7, 7)]` | Droni: `[(9, 4), (8, 4), (9, 3), (7, 4)]`

```text
Step   1: pos=[(9, 4), (8, 4), (9, 3), (7, 4)] | azioni=[D0:Giu, D1:Fermo, D2:Giu, D3:Fermo]
          -> nuove pos=[(9, 5), (8, 4), (9, 4), (7, 4)] (droni fermi: ['D1', 'D3'])
Step   2: pos=[(9, 5), (8, 4), (9, 4), (7, 4)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(9, 6), (8, 4), (9, 5), (7, 5)] (D1 da (8, 4) colpisce la montagna in (8, 5))
Step   3: pos=[(9, 6), (8, 4), (9, 5), (7, 5)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(9, 7), (8, 4), (9, 6), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5))
Step   4: pos=[(9, 7), (8, 4), (9, 6), (7, 6)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 7), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
Step   5: pos=[(9, 8), (8, 4), (9, 7), (7, 6)] | azioni=[D0:arrivato, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 8), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
Step   6: pos=[(9, 8), (8, 4), (9, 8), (7, 6)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 8), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
Step   7: pos=[(9, 8), (8, 4), (9, 8), (7, 6)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 8), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
Step   8: pos=[(9, 8), (8, 4), (9, 8), (7, 6)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 8), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
  ... (dal passo 9 al 97 si ripete lo stesso comportamento) ...
Step  98: pos=[(9, 8), (8, 4), (9, 8), (7, 6)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 8), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
Step  99: pos=[(9, 8), (8, 4), (9, 8), (7, 6)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 8), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
Step 100: pos=[(9, 8), (8, 4), (9, 8), (7, 6)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 8), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
```

- Esito: fallimento per timeout a 100 step (reward: -1967.0, droni arrivati: 2/4, precedenze attivate: 0)
- Comportamento: i droni rimangono effettivamente bloccati
  - Drone D1: resta fermo nella cella (8, 4)
  - Drone D3: resta fermo nella cella (7, 6)

### [PPO - seed 42 - SENZA PRECEDENZA] Caso 1a - Contesa della stessa casella ai lati dell'hangar (2 droni)
Hangar in (4,8). I droni D0 e D2 sono gia arrivati, mentre D1 in (5,7) e D3 in (4,6) cercano entrambi di passare per la casella (4,7) sopra l'hangar.
- Hangar: `(4, 8)` | Montagne: `[(1, 1), (8, 1), (1, 4), (8, 4)]` | Droni: `[(4, 8), (5, 7), (4, 8), (4, 6)]`

```text
Step   1: pos=[(4, 8), (5, 7), (4, 8), (4, 6)] | azioni=[D0:arrivato, D1:Sinistra, D2:arrivato, D3:Giu]
          -> nuove pos=[(4, 8), (5, 7), (4, 8), (4, 6)] (scontro tra D1(5, 7) e D3(4, 6) sulla cella (4, 7) a lato dell'hangar)
Step   2: pos=[(4, 8), (5, 7), (4, 8), (4, 6)] | azioni=[D0:arrivato, D1:Sinistra, D2:arrivato, D3:Giu]
          -> nuove pos=[(4, 8), (5, 7), (4, 8), (4, 6)] (scontro tra D1(5, 7) e D3(4, 6) sulla cella (4, 7) a lato dell'hangar)
Step   3: pos=[(4, 8), (5, 7), (4, 8), (4, 6)] | azioni=[D0:arrivato, D1:Sinistra, D2:arrivato, D3:Giu]
          -> nuove pos=[(4, 8), (5, 7), (4, 8), (4, 6)] (scontro tra D1(5, 7) e D3(4, 6) sulla cella (4, 7) a lato dell'hangar)
Step   4: pos=[(4, 8), (5, 7), (4, 8), (4, 6)] | azioni=[D0:arrivato, D1:Sinistra, D2:arrivato, D3:Giu]
          -> nuove pos=[(4, 8), (5, 7), (4, 8), (4, 6)] (scontro tra D1(5, 7) e D3(4, 6) sulla cella (4, 7) a lato dell'hangar)
Step   5: pos=[(4, 8), (5, 7), (4, 8), (4, 6)] | azioni=[D0:arrivato, D1:Sinistra, D2:arrivato, D3:Giu]
          -> nuove pos=[(4, 8), (5, 7), (4, 8), (4, 6)] (scontro tra D1(5, 7) e D3(4, 6) sulla cella (4, 7) a lato dell'hangar)
Step   6: pos=[(4, 8), (5, 7), (4, 8), (4, 6)] | azioni=[D0:arrivato, D1:Sinistra, D2:arrivato, D3:Giu]
          -> nuove pos=[(4, 8), (5, 7), (4, 8), (4, 6)] (scontro tra D1(5, 7) e D3(4, 6) sulla cella (4, 7) a lato dell'hangar)
Step   7: pos=[(4, 8), (5, 7), (4, 8), (4, 6)] | azioni=[D0:arrivato, D1:Sinistra, D2:arrivato, D3:Giu]
          -> nuove pos=[(4, 8), (5, 7), (4, 8), (4, 6)] (scontro tra D1(5, 7) e D3(4, 6) sulla cella (4, 7) a lato dell'hangar)
Step   8: pos=[(4, 8), (5, 7), (4, 8), (4, 6)] | azioni=[D0:arrivato, D1:Sinistra, D2:arrivato, D3:Giu]
          -> nuove pos=[(4, 8), (5, 7), (4, 8), (4, 6)] (scontro tra D1(5, 7) e D3(4, 6) sulla cella (4, 7) a lato dell'hangar)
  ... (dal passo 9 al 97 si ripete lo stesso comportamento) ...
Step  98: pos=[(4, 8), (5, 7), (4, 8), (4, 6)] | azioni=[D0:arrivato, D1:Sinistra, D2:arrivato, D3:Giu]
          -> nuove pos=[(4, 8), (5, 7), (4, 8), (4, 6)] (scontro tra D1(5, 7) e D3(4, 6) sulla cella (4, 7) a lato dell'hangar)
Step  99: pos=[(4, 8), (5, 7), (4, 8), (4, 6)] | azioni=[D0:arrivato, D1:Sinistra, D2:arrivato, D3:Giu]
          -> nuove pos=[(4, 8), (5, 7), (4, 8), (4, 6)] (scontro tra D1(5, 7) e D3(4, 6) sulla cella (4, 7) a lato dell'hangar)
Step 100: pos=[(4, 8), (5, 7), (4, 8), (4, 6)] | azioni=[D0:arrivato, D1:Sinistra, D2:arrivato, D3:Giu]
          -> nuove pos=[(4, 8), (5, 7), (4, 8), (4, 6)] (scontro tra D1(5, 7) e D3(4, 6) sulla cella (4, 7) a lato dell'hangar)
```

- Esito: fallimento per timeout a 100 step (reward: -2200.0, droni arrivati: 2/4, precedenze attivate: 0)
- Comportamento: i droni rimangono effettivamente bloccati
  - Drone D1: resta fermo nella cella (5, 7)
  - Drone D3: resta fermo nella cella (4, 6)

### [PPO - seed 42 - CON PRECEDENZA] Caso 1a - Contesa della stessa casella ai lati dell'hangar (2 droni)
Hangar in (4,8). I droni D0 e D2 sono gia arrivati, mentre D1 in (5,7) e D3 in (4,6) cercano entrambi di passare per la casella (4,7) sopra l'hangar.
- Hangar: `(4, 8)` | Montagne: `[(1, 1), (8, 1), (1, 4), (8, 4)]` | Droni: `[(4, 8), (5, 7), (4, 8), (4, 6)]`

```text
Step   1: pos=[(4, 8), (5, 7), (4, 8), (4, 6)] | azioni=[D0:arrivato, D1:Sinistra, D2:arrivato, D3:Giu]
          -> nuove pos=[(4, 8), (4, 7), (4, 8), (4, 6)] (precedenza su (4, 7): passa D1(5, 7) (dist=2), attende D3(4, 6) (dist=2))
Step   2: pos=[(4, 8), (4, 7), (4, 8), (4, 6)] | azioni=[D0:arrivato, D1:Sinistra, D2:arrivato, D3:Giu]
          -> nuove pos=[(4, 8), (3, 7), (4, 8), (4, 7)] (droni mossi: [1, 3])
Step   3: pos=[(4, 8), (3, 7), (4, 8), (4, 7)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Sinistra]
          -> nuove pos=[(4, 8), (3, 8), (4, 8), (3, 7)] (droni mossi: [1, 3])
Step   4: pos=[(4, 8), (3, 8), (4, 8), (3, 7)] | azioni=[D0:arrivato, D1:Destra, D2:arrivato, D3:Destra]
          -> nuove pos=[(4, 8), (4, 8), (4, 8), (4, 7)] (droni mossi: [1, 3])
Step   5: pos=[(4, 8), (4, 8), (4, 8), (4, 7)] | azioni=[D0:arrivato, D1:arrivato, D2:arrivato, D3:Sinistra]
          -> nuove pos=[(4, 8), (4, 8), (4, 8), (3, 7)] (droni mossi: [3])
Step   6: pos=[(4, 8), (4, 8), (4, 8), (3, 7)] | azioni=[D0:arrivato, D1:arrivato, D2:arrivato, D3:Giu]
          -> nuove pos=[(4, 8), (4, 8), (4, 8), (3, 8)] (droni mossi: [3])
Step   7: pos=[(4, 8), (4, 8), (4, 8), (3, 8)] | azioni=[D0:arrivato, D1:arrivato, D2:arrivato, D3:Destra]
          -> nuove pos=[(4, 8), (4, 8), (4, 8), (4, 8)] (droni mossi: [3])
```

- Esito: completato in 7 step (reward: 191.0, precedenze attivate: 1)

### [PPO - seed 42 - SENZA PRECEDENZA] Caso 1b - Contesa ai lati dell'hangar con 4 droni
Hangar in (5,5) con montagne sopra (5,4) e sotto (5,6). D0(3,5) e D1(4,4) puntano al lato sinistro (4,5), mentre D2(7,5) e D3(6,6) puntano al lato destro (6,5).
- Hangar: `(5, 5)` | Montagne: `[(5, 4), (5, 6), (1, 1), (8, 8)]` | Droni: `[(3, 5), (4, 4), (7, 5), (6, 6)]`

```text
Step   1: pos=[(3, 5), (4, 4), (7, 5), (6, 6)] | azioni=[D0:Destra, D1:Destra, D2:Sinistra, D3:Sinistra]
          -> nuove pos=[(4, 5), (4, 4), (6, 5), (6, 6)] (D1 da (4, 4) colpisce la montagna in (5, 4) | D3 da (6, 6) colpisce la montagna in (5, 6))
Step   2: pos=[(4, 5), (4, 4), (6, 5), (6, 6)] | azioni=[D0:Destra, D1:Giu, D2:Sinistra, D3:Sinistra]
          -> nuove pos=[(5, 5), (4, 5), (5, 5), (6, 6)] (D3 da (6, 6) colpisce la montagna in (5, 6))
Step   3: pos=[(5, 5), (4, 5), (5, 5), (6, 6)] | azioni=[D0:arrivato, D1:Destra, D2:arrivato, D3:Sinistra]
          -> nuove pos=[(5, 5), (5, 5), (5, 5), (6, 6)] (D3 da (6, 6) colpisce la montagna in (5, 6))
Step   4: pos=[(5, 5), (5, 5), (5, 5), (6, 6)] | azioni=[D0:arrivato, D1:arrivato, D2:arrivato, D3:Sinistra]
          -> nuove pos=[(5, 5), (5, 5), (5, 5), (6, 6)] (D3 da (6, 6) colpisce la montagna in (5, 6))
Step   5: pos=[(5, 5), (5, 5), (5, 5), (6, 6)] | azioni=[D0:arrivato, D1:arrivato, D2:arrivato, D3:Sinistra]
          -> nuove pos=[(5, 5), (5, 5), (5, 5), (6, 6)] (D3 da (6, 6) colpisce la montagna in (5, 6))
Step   6: pos=[(5, 5), (5, 5), (5, 5), (6, 6)] | azioni=[D0:arrivato, D1:arrivato, D2:arrivato, D3:Sinistra]
          -> nuove pos=[(5, 5), (5, 5), (5, 5), (6, 6)] (D3 da (6, 6) colpisce la montagna in (5, 6))
Step   7: pos=[(5, 5), (5, 5), (5, 5), (6, 6)] | azioni=[D0:arrivato, D1:arrivato, D2:arrivato, D3:Sinistra]
          -> nuove pos=[(5, 5), (5, 5), (5, 5), (6, 6)] (D3 da (6, 6) colpisce la montagna in (5, 6))
Step   8: pos=[(5, 5), (5, 5), (5, 5), (6, 6)] | azioni=[D0:arrivato, D1:arrivato, D2:arrivato, D3:Sinistra]
          -> nuove pos=[(5, 5), (5, 5), (5, 5), (6, 6)] (D3 da (6, 6) colpisce la montagna in (5, 6))
  ... (dal passo 9 al 97 si ripete lo stesso comportamento) ...
Step  98: pos=[(5, 5), (5, 5), (5, 5), (6, 6)] | azioni=[D0:arrivato, D1:arrivato, D2:arrivato, D3:Sinistra]
          -> nuove pos=[(5, 5), (5, 5), (5, 5), (6, 6)] (D3 da (6, 6) colpisce la montagna in (5, 6))
Step  99: pos=[(5, 5), (5, 5), (5, 5), (6, 6)] | azioni=[D0:arrivato, D1:arrivato, D2:arrivato, D3:Sinistra]
          -> nuove pos=[(5, 5), (5, 5), (5, 5), (6, 6)] (D3 da (6, 6) colpisce la montagna in (5, 6))
Step 100: pos=[(5, 5), (5, 5), (5, 5), (6, 6)] | azioni=[D0:arrivato, D1:arrivato, D2:arrivato, D3:Sinistra]
          -> nuove pos=[(5, 5), (5, 5), (5, 5), (6, 6)] (D3 da (6, 6) colpisce la montagna in (5, 6))
```

- Esito: fallimento per timeout a 100 step (reward: -814.0, droni arrivati: 3/4, precedenze attivate: 0)
- Comportamento: i droni rimangono effettivamente bloccati
  - Drone D3: resta fermo nella cella (6, 6)

### [PPO - seed 42 - CON PRECEDENZA] Caso 1b - Contesa ai lati dell'hangar con 4 droni
Hangar in (5,5) con montagne sopra (5,4) e sotto (5,6). D0(3,5) e D1(4,4) puntano al lato sinistro (4,5), mentre D2(7,5) e D3(6,6) puntano al lato destro (6,5).
- Hangar: `(5, 5)` | Montagne: `[(5, 4), (5, 6), (1, 1), (8, 8)]` | Droni: `[(3, 5), (4, 4), (7, 5), (6, 6)]`

```text
Step   1: pos=[(3, 5), (4, 4), (7, 5), (6, 6)] | azioni=[D0:Destra, D1:Destra, D2:Sinistra, D3:Sinistra]
          -> nuove pos=[(4, 5), (4, 4), (6, 5), (6, 6)] (D1 da (4, 4) colpisce la montagna in (5, 4) | D3 da (6, 6) colpisce la montagna in (5, 6))
Step   2: pos=[(4, 5), (4, 4), (6, 5), (6, 6)] | azioni=[D0:Destra, D1:Giu, D2:Sinistra, D3:Sinistra]
          -> nuove pos=[(5, 5), (4, 5), (5, 5), (6, 6)] (D3 da (6, 6) colpisce la montagna in (5, 6))
Step   3: pos=[(5, 5), (4, 5), (5, 5), (6, 6)] | azioni=[D0:arrivato, D1:Destra, D2:arrivato, D3:Sinistra]
          -> nuove pos=[(5, 5), (5, 5), (5, 5), (6, 6)] (D3 da (6, 6) colpisce la montagna in (5, 6))
Step   4: pos=[(5, 5), (5, 5), (5, 5), (6, 6)] | azioni=[D0:arrivato, D1:arrivato, D2:arrivato, D3:Sinistra]
          -> nuove pos=[(5, 5), (5, 5), (5, 5), (6, 6)] (D3 da (6, 6) colpisce la montagna in (5, 6))
Step   5: pos=[(5, 5), (5, 5), (5, 5), (6, 6)] | azioni=[D0:arrivato, D1:arrivato, D2:arrivato, D3:Sinistra]
          -> nuove pos=[(5, 5), (5, 5), (5, 5), (6, 6)] (D3 da (6, 6) colpisce la montagna in (5, 6))
Step   6: pos=[(5, 5), (5, 5), (5, 5), (6, 6)] | azioni=[D0:arrivato, D1:arrivato, D2:arrivato, D3:Sinistra]
          -> nuove pos=[(5, 5), (5, 5), (5, 5), (6, 6)] (D3 da (6, 6) colpisce la montagna in (5, 6))
Step   7: pos=[(5, 5), (5, 5), (5, 5), (6, 6)] | azioni=[D0:arrivato, D1:arrivato, D2:arrivato, D3:Sinistra]
          -> nuove pos=[(5, 5), (5, 5), (5, 5), (6, 6)] (D3 da (6, 6) colpisce la montagna in (5, 6))
Step   8: pos=[(5, 5), (5, 5), (5, 5), (6, 6)] | azioni=[D0:arrivato, D1:arrivato, D2:arrivato, D3:Sinistra]
          -> nuove pos=[(5, 5), (5, 5), (5, 5), (6, 6)] (D3 da (6, 6) colpisce la montagna in (5, 6))
  ... (dal passo 9 al 97 si ripete lo stesso comportamento) ...
Step  98: pos=[(5, 5), (5, 5), (5, 5), (6, 6)] | azioni=[D0:arrivato, D1:arrivato, D2:arrivato, D3:Sinistra]
          -> nuove pos=[(5, 5), (5, 5), (5, 5), (6, 6)] (D3 da (6, 6) colpisce la montagna in (5, 6))
Step  99: pos=[(5, 5), (5, 5), (5, 5), (6, 6)] | azioni=[D0:arrivato, D1:arrivato, D2:arrivato, D3:Sinistra]
          -> nuove pos=[(5, 5), (5, 5), (5, 5), (6, 6)] (D3 da (6, 6) colpisce la montagna in (5, 6))
Step 100: pos=[(5, 5), (5, 5), (5, 5), (6, 6)] | azioni=[D0:arrivato, D1:arrivato, D2:arrivato, D3:Sinistra]
          -> nuove pos=[(5, 5), (5, 5), (5, 5), (6, 6)] (D3 da (6, 6) colpisce la montagna in (5, 6))
```

- Esito: fallimento per timeout a 100 step (reward: -814.0, droni arrivati: 3/4, precedenze attivate: 0)
- Comportamento: i droni rimangono effettivamente bloccati
  - Drone D3: resta fermo nella cella (6, 6)

### [PPO - seed 42 - SENZA PRECEDENZA] Caso 2a - Montagne a 1 cella dal bordo sinistro
Montagne in (1,5), (2,5), (3,5), (4,5) che lasciano solo la cella (0,5) libera sul bordo sinistro. Hangar in (0,7) e droni in (0,4), (1,4), (0,3) e (2,4) che devono passare da (0,5).
- Hangar: `(0, 7)` | Montagne: `[(1, 5), (2, 5), (3, 5), (4, 5)]` | Droni: `[(0, 4), (1, 4), (0, 3), (2, 4)]`

```text
Step   1: pos=[(0, 4), (1, 4), (0, 3), (2, 4)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 5), (1, 4), (0, 4), (2, 4)] (D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5))
Step   2: pos=[(0, 5), (1, 4), (0, 4), (2, 4)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 6), (1, 4), (0, 5), (2, 4)] (D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5))
Step   3: pos=[(0, 6), (1, 4), (0, 5), (2, 4)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 7), (1, 4), (0, 6), (2, 4)] (D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5))
Step   4: pos=[(0, 7), (1, 4), (0, 6), (2, 4)] | azioni=[D0:arrivato, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 7), (1, 4), (0, 7), (2, 4)] (D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5))
Step   5: pos=[(0, 7), (1, 4), (0, 7), (2, 4)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(0, 7), (1, 4), (0, 7), (2, 4)] (D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5))
Step   6: pos=[(0, 7), (1, 4), (0, 7), (2, 4)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(0, 7), (1, 4), (0, 7), (2, 4)] (D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5))
Step   7: pos=[(0, 7), (1, 4), (0, 7), (2, 4)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(0, 7), (1, 4), (0, 7), (2, 4)] (D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5))
Step   8: pos=[(0, 7), (1, 4), (0, 7), (2, 4)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(0, 7), (1, 4), (0, 7), (2, 4)] (D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5))
  ... (dal passo 9 al 97 si ripete lo stesso comportamento) ...
Step  98: pos=[(0, 7), (1, 4), (0, 7), (2, 4)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(0, 7), (1, 4), (0, 7), (2, 4)] (D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5))
Step  99: pos=[(0, 7), (1, 4), (0, 7), (2, 4)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(0, 7), (1, 4), (0, 7), (2, 4)] (D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5))
Step 100: pos=[(0, 7), (1, 4), (0, 7), (2, 4)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(0, 7), (1, 4), (0, 7), (2, 4)] (D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5))
```

- Esito: fallimento per timeout a 100 step (reward: -2005.0, droni arrivati: 2/4, precedenze attivate: 0)
- Comportamento: i droni rimangono effettivamente bloccati
  - Drone D1: resta fermo nella cella (1, 4)
  - Drone D3: resta fermo nella cella (2, 4)

### [PPO - seed 42 - CON PRECEDENZA] Caso 2a - Montagne a 1 cella dal bordo sinistro
Montagne in (1,5), (2,5), (3,5), (4,5) che lasciano solo la cella (0,5) libera sul bordo sinistro. Hangar in (0,7) e droni in (0,4), (1,4), (0,3) e (2,4) che devono passare da (0,5).
- Hangar: `(0, 7)` | Montagne: `[(1, 5), (2, 5), (3, 5), (4, 5)]` | Droni: `[(0, 4), (1, 4), (0, 3), (2, 4)]`

```text
Step   1: pos=[(0, 4), (1, 4), (0, 3), (2, 4)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 5), (1, 4), (0, 4), (2, 4)] (D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5))
Step   2: pos=[(0, 5), (1, 4), (0, 4), (2, 4)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 6), (1, 4), (0, 5), (2, 4)] (D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5))
Step   3: pos=[(0, 6), (1, 4), (0, 5), (2, 4)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 7), (1, 4), (0, 6), (2, 4)] (D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5))
Step   4: pos=[(0, 7), (1, 4), (0, 6), (2, 4)] | azioni=[D0:arrivato, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 7), (1, 4), (0, 7), (2, 4)] (D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5))
Step   5: pos=[(0, 7), (1, 4), (0, 7), (2, 4)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(0, 7), (1, 4), (0, 7), (2, 4)] (D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5))
Step   6: pos=[(0, 7), (1, 4), (0, 7), (2, 4)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(0, 7), (1, 4), (0, 7), (2, 4)] (D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5))
Step   7: pos=[(0, 7), (1, 4), (0, 7), (2, 4)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(0, 7), (1, 4), (0, 7), (2, 4)] (D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5))
Step   8: pos=[(0, 7), (1, 4), (0, 7), (2, 4)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(0, 7), (1, 4), (0, 7), (2, 4)] (D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5))
  ... (dal passo 9 al 97 si ripete lo stesso comportamento) ...
Step  98: pos=[(0, 7), (1, 4), (0, 7), (2, 4)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(0, 7), (1, 4), (0, 7), (2, 4)] (D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5))
Step  99: pos=[(0, 7), (1, 4), (0, 7), (2, 4)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(0, 7), (1, 4), (0, 7), (2, 4)] (D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5))
Step 100: pos=[(0, 7), (1, 4), (0, 7), (2, 4)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(0, 7), (1, 4), (0, 7), (2, 4)] (D1 da (1, 4) colpisce la montagna in (1, 5) | D3 da (2, 4) colpisce la montagna in (2, 5))
```

- Esito: fallimento per timeout a 100 step (reward: -2005.0, droni arrivati: 2/4, precedenze attivate: 0)
- Comportamento: i droni rimangono effettivamente bloccati
  - Drone D1: resta fermo nella cella (1, 4)
  - Drone D3: resta fermo nella cella (2, 4)

### [PPO - seed 42 - SENZA PRECEDENZA] Caso 2b - Montagne a 1 cella dal bordo superiore
Montagne in (5,1), (5,2), (5,3), (5,4) che lasciano solo la cella (5,0) libera sul bordo in alto. Hangar in (7,0) e droni in (4,0), (4,1), (3,0), (4,2) che devono passare da (5,0).
- Hangar: `(7, 0)` | Montagne: `[(5, 1), (5, 2), (5, 3), (5, 4)]` | Droni: `[(4, 0), (4, 1), (3, 0), (4, 2)]`

```text
Step   1: pos=[(4, 0), (4, 1), (3, 0), (4, 2)] | azioni=[D0:Destra, D1:Destra, D2:Destra, D3:Destra]
          -> nuove pos=[(5, 0), (4, 1), (4, 0), (4, 2)] (D1 da (4, 1) colpisce la montagna in (5, 1) | D3 da (4, 2) colpisce la montagna in (5, 2))
Step   2: pos=[(5, 0), (4, 1), (4, 0), (4, 2)] | azioni=[D0:Destra, D1:Destra, D2:Destra, D3:Destra]
          -> nuove pos=[(6, 0), (4, 1), (5, 0), (4, 2)] (D1 da (4, 1) colpisce la montagna in (5, 1) | D3 da (4, 2) colpisce la montagna in (5, 2))
Step   3: pos=[(6, 0), (4, 1), (5, 0), (4, 2)] | azioni=[D0:Destra, D1:Destra, D2:Destra, D3:Destra]
          -> nuove pos=[(7, 0), (4, 1), (6, 0), (4, 2)] (D1 da (4, 1) colpisce la montagna in (5, 1) | D3 da (4, 2) colpisce la montagna in (5, 2))
Step   4: pos=[(7, 0), (4, 1), (6, 0), (4, 2)] | azioni=[D0:arrivato, D1:Destra, D2:Destra, D3:Destra]
          -> nuove pos=[(7, 0), (4, 1), (7, 0), (4, 2)] (D1 da (4, 1) colpisce la montagna in (5, 1) | D3 da (4, 2) colpisce la montagna in (5, 2))
Step   5: pos=[(7, 0), (4, 1), (7, 0), (4, 2)] | azioni=[D0:arrivato, D1:Destra, D2:arrivato, D3:Destra]
          -> nuove pos=[(7, 0), (4, 1), (7, 0), (4, 2)] (D1 da (4, 1) colpisce la montagna in (5, 1) | D3 da (4, 2) colpisce la montagna in (5, 2))
Step   6: pos=[(7, 0), (4, 1), (7, 0), (4, 2)] | azioni=[D0:arrivato, D1:Destra, D2:arrivato, D3:Destra]
          -> nuove pos=[(7, 0), (4, 1), (7, 0), (4, 2)] (D1 da (4, 1) colpisce la montagna in (5, 1) | D3 da (4, 2) colpisce la montagna in (5, 2))
Step   7: pos=[(7, 0), (4, 1), (7, 0), (4, 2)] | azioni=[D0:arrivato, D1:Destra, D2:arrivato, D3:Destra]
          -> nuove pos=[(7, 0), (4, 1), (7, 0), (4, 2)] (D1 da (4, 1) colpisce la montagna in (5, 1) | D3 da (4, 2) colpisce la montagna in (5, 2))
Step   8: pos=[(7, 0), (4, 1), (7, 0), (4, 2)] | azioni=[D0:arrivato, D1:Destra, D2:arrivato, D3:Destra]
          -> nuove pos=[(7, 0), (4, 1), (7, 0), (4, 2)] (D1 da (4, 1) colpisce la montagna in (5, 1) | D3 da (4, 2) colpisce la montagna in (5, 2))
  ... (dal passo 9 al 97 si ripete lo stesso comportamento) ...
Step  98: pos=[(7, 0), (4, 1), (7, 0), (4, 2)] | azioni=[D0:arrivato, D1:Destra, D2:arrivato, D3:Destra]
          -> nuove pos=[(7, 0), (4, 1), (7, 0), (4, 2)] (D1 da (4, 1) colpisce la montagna in (5, 1) | D3 da (4, 2) colpisce la montagna in (5, 2))
Step  99: pos=[(7, 0), (4, 1), (7, 0), (4, 2)] | azioni=[D0:arrivato, D1:Destra, D2:arrivato, D3:Destra]
          -> nuove pos=[(7, 0), (4, 1), (7, 0), (4, 2)] (D1 da (4, 1) colpisce la montagna in (5, 1) | D3 da (4, 2) colpisce la montagna in (5, 2))
Step 100: pos=[(7, 0), (4, 1), (7, 0), (4, 2)] | azioni=[D0:arrivato, D1:Destra, D2:arrivato, D3:Destra]
          -> nuove pos=[(7, 0), (4, 1), (7, 0), (4, 2)] (D1 da (4, 1) colpisce la montagna in (5, 1) | D3 da (4, 2) colpisce la montagna in (5, 2))
```

- Esito: fallimento per timeout a 100 step (reward: -2005.0, droni arrivati: 2/4, precedenze attivate: 0)
- Comportamento: i droni rimangono effettivamente bloccati
  - Drone D1: resta fermo nella cella (4, 1)
  - Drone D3: resta fermo nella cella (4, 2)

### [PPO - seed 42 - CON PRECEDENZA] Caso 2b - Montagne a 1 cella dal bordo superiore
Montagne in (5,1), (5,2), (5,3), (5,4) che lasciano solo la cella (5,0) libera sul bordo in alto. Hangar in (7,0) e droni in (4,0), (4,1), (3,0), (4,2) che devono passare da (5,0).
- Hangar: `(7, 0)` | Montagne: `[(5, 1), (5, 2), (5, 3), (5, 4)]` | Droni: `[(4, 0), (4, 1), (3, 0), (4, 2)]`

```text
Step   1: pos=[(4, 0), (4, 1), (3, 0), (4, 2)] | azioni=[D0:Destra, D1:Destra, D2:Destra, D3:Destra]
          -> nuove pos=[(5, 0), (4, 1), (4, 0), (4, 2)] (D1 da (4, 1) colpisce la montagna in (5, 1) | D3 da (4, 2) colpisce la montagna in (5, 2))
Step   2: pos=[(5, 0), (4, 1), (4, 0), (4, 2)] | azioni=[D0:Destra, D1:Destra, D2:Destra, D3:Destra]
          -> nuove pos=[(6, 0), (4, 1), (5, 0), (4, 2)] (D1 da (4, 1) colpisce la montagna in (5, 1) | D3 da (4, 2) colpisce la montagna in (5, 2))
Step   3: pos=[(6, 0), (4, 1), (5, 0), (4, 2)] | azioni=[D0:Destra, D1:Destra, D2:Destra, D3:Destra]
          -> nuove pos=[(7, 0), (4, 1), (6, 0), (4, 2)] (D1 da (4, 1) colpisce la montagna in (5, 1) | D3 da (4, 2) colpisce la montagna in (5, 2))
Step   4: pos=[(7, 0), (4, 1), (6, 0), (4, 2)] | azioni=[D0:arrivato, D1:Destra, D2:Destra, D3:Destra]
          -> nuove pos=[(7, 0), (4, 1), (7, 0), (4, 2)] (D1 da (4, 1) colpisce la montagna in (5, 1) | D3 da (4, 2) colpisce la montagna in (5, 2))
Step   5: pos=[(7, 0), (4, 1), (7, 0), (4, 2)] | azioni=[D0:arrivato, D1:Destra, D2:arrivato, D3:Destra]
          -> nuove pos=[(7, 0), (4, 1), (7, 0), (4, 2)] (D1 da (4, 1) colpisce la montagna in (5, 1) | D3 da (4, 2) colpisce la montagna in (5, 2))
Step   6: pos=[(7, 0), (4, 1), (7, 0), (4, 2)] | azioni=[D0:arrivato, D1:Destra, D2:arrivato, D3:Destra]
          -> nuove pos=[(7, 0), (4, 1), (7, 0), (4, 2)] (D1 da (4, 1) colpisce la montagna in (5, 1) | D3 da (4, 2) colpisce la montagna in (5, 2))
Step   7: pos=[(7, 0), (4, 1), (7, 0), (4, 2)] | azioni=[D0:arrivato, D1:Destra, D2:arrivato, D3:Destra]
          -> nuove pos=[(7, 0), (4, 1), (7, 0), (4, 2)] (D1 da (4, 1) colpisce la montagna in (5, 1) | D3 da (4, 2) colpisce la montagna in (5, 2))
Step   8: pos=[(7, 0), (4, 1), (7, 0), (4, 2)] | azioni=[D0:arrivato, D1:Destra, D2:arrivato, D3:Destra]
          -> nuove pos=[(7, 0), (4, 1), (7, 0), (4, 2)] (D1 da (4, 1) colpisce la montagna in (5, 1) | D3 da (4, 2) colpisce la montagna in (5, 2))
  ... (dal passo 9 al 97 si ripete lo stesso comportamento) ...
Step  98: pos=[(7, 0), (4, 1), (7, 0), (4, 2)] | azioni=[D0:arrivato, D1:Destra, D2:arrivato, D3:Destra]
          -> nuove pos=[(7, 0), (4, 1), (7, 0), (4, 2)] (D1 da (4, 1) colpisce la montagna in (5, 1) | D3 da (4, 2) colpisce la montagna in (5, 2))
Step  99: pos=[(7, 0), (4, 1), (7, 0), (4, 2)] | azioni=[D0:arrivato, D1:Destra, D2:arrivato, D3:Destra]
          -> nuove pos=[(7, 0), (4, 1), (7, 0), (4, 2)] (D1 da (4, 1) colpisce la montagna in (5, 1) | D3 da (4, 2) colpisce la montagna in (5, 2))
Step 100: pos=[(7, 0), (4, 1), (7, 0), (4, 2)] | azioni=[D0:arrivato, D1:Destra, D2:arrivato, D3:Destra]
          -> nuove pos=[(7, 0), (4, 1), (7, 0), (4, 2)] (D1 da (4, 1) colpisce la montagna in (5, 1) | D3 da (4, 2) colpisce la montagna in (5, 2))
```

- Esito: fallimento per timeout a 100 step (reward: -2005.0, droni arrivati: 2/4, precedenze attivate: 0)
- Comportamento: i droni rimangono effettivamente bloccati
  - Drone D1: resta fermo nella cella (4, 1)
  - Drone D3: resta fermo nella cella (4, 2)

### [PPO - seed 42 - SENZA PRECEDENZA] Caso 2c - Passaggio di 1 cella lungo il bordo destro
Montagne in (8,5), (8,6), (8,7), (7,7) che lasciano un passaggio di 1 cella sul bordo destro per arrivare all'hangar in (9,8). Droni in partenza da (9,4), (8,4), (9,3), (7,4).
- Hangar: `(9, 8)` | Montagne: `[(8, 5), (8, 6), (8, 7), (7, 7)]` | Droni: `[(9, 4), (8, 4), (9, 3), (7, 4)]`

```text
Step   1: pos=[(9, 4), (8, 4), (9, 3), (7, 4)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(9, 5), (8, 4), (9, 4), (7, 5)] (D1 da (8, 4) colpisce la montagna in (8, 5))
Step   2: pos=[(9, 5), (8, 4), (9, 4), (7, 5)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(9, 6), (8, 4), (9, 5), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5))
Step   3: pos=[(9, 6), (8, 4), (9, 5), (7, 6)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(9, 7), (8, 4), (9, 6), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
Step   4: pos=[(9, 7), (8, 4), (9, 6), (7, 6)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 7), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
Step   5: pos=[(9, 8), (8, 4), (9, 7), (7, 6)] | azioni=[D0:arrivato, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 8), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
Step   6: pos=[(9, 8), (8, 4), (9, 8), (7, 6)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 8), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
Step   7: pos=[(9, 8), (8, 4), (9, 8), (7, 6)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 8), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
Step   8: pos=[(9, 8), (8, 4), (9, 8), (7, 6)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 8), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
  ... (dal passo 9 al 97 si ripete lo stesso comportamento) ...
Step  98: pos=[(9, 8), (8, 4), (9, 8), (7, 6)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 8), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
Step  99: pos=[(9, 8), (8, 4), (9, 8), (7, 6)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 8), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
Step 100: pos=[(9, 8), (8, 4), (9, 8), (7, 6)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 8), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
```

- Esito: fallimento per timeout a 100 step (reward: -1987.0, droni arrivati: 2/4, precedenze attivate: 0)
- Comportamento: i droni rimangono effettivamente bloccati
  - Drone D1: resta fermo nella cella (8, 4)
  - Drone D3: resta fermo nella cella (7, 6)

### [PPO - seed 42 - CON PRECEDENZA] Caso 2c - Passaggio di 1 cella lungo il bordo destro
Montagne in (8,5), (8,6), (8,7), (7,7) che lasciano un passaggio di 1 cella sul bordo destro per arrivare all'hangar in (9,8). Droni in partenza da (9,4), (8,4), (9,3), (7,4).
- Hangar: `(9, 8)` | Montagne: `[(8, 5), (8, 6), (8, 7), (7, 7)]` | Droni: `[(9, 4), (8, 4), (9, 3), (7, 4)]`

```text
Step   1: pos=[(9, 4), (8, 4), (9, 3), (7, 4)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(9, 5), (8, 4), (9, 4), (7, 5)] (D1 da (8, 4) colpisce la montagna in (8, 5))
Step   2: pos=[(9, 5), (8, 4), (9, 4), (7, 5)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(9, 6), (8, 4), (9, 5), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5))
Step   3: pos=[(9, 6), (8, 4), (9, 5), (7, 6)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(9, 7), (8, 4), (9, 6), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
Step   4: pos=[(9, 7), (8, 4), (9, 6), (7, 6)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 7), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
Step   5: pos=[(9, 8), (8, 4), (9, 7), (7, 6)] | azioni=[D0:arrivato, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 8), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
Step   6: pos=[(9, 8), (8, 4), (9, 8), (7, 6)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 8), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
Step   7: pos=[(9, 8), (8, 4), (9, 8), (7, 6)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 8), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
Step   8: pos=[(9, 8), (8, 4), (9, 8), (7, 6)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 8), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
  ... (dal passo 9 al 97 si ripete lo stesso comportamento) ...
Step  98: pos=[(9, 8), (8, 4), (9, 8), (7, 6)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 8), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
Step  99: pos=[(9, 8), (8, 4), (9, 8), (7, 6)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 8), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
Step 100: pos=[(9, 8), (8, 4), (9, 8), (7, 6)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(9, 8), (8, 4), (9, 8), (7, 6)] (D1 da (8, 4) colpisce la montagna in (8, 5) | D3 da (7, 6) colpisce la montagna in (7, 7))
```

- Esito: fallimento per timeout a 100 step (reward: -1987.0, droni arrivati: 2/4, precedenze attivate: 0)
- Comportamento: i droni rimangono effettivamente bloccati
  - Drone D1: resta fermo nella cella (8, 4)
  - Drone D3: resta fermo nella cella (7, 6)

### Riepilogo confronto scenari fissi (Senza vs Con Precedenza)

| Algoritmo | Scenario | Senza Precedenza | Con Precedenza | Scontri Vertice (Prima -> Dopo) | Precedenze Attivate |
|:---:|:---|:---:|:---:|:---:|:---:|
| MAPPO | Caso 1a - Contesa della stessa casella ai lati dell'hangar (2 droni) | FAIL (3/4 arr.) | **FAIL (3/4 arr.)** | 0 -> 0 | 0 |
| MAPPO | Caso 1b - Contesa ai lati dell'hangar con 4 droni | FAIL (3/4 arr.) | **FAIL (1/4 arr.)** | 1 -> 98 | 1 |
| MAPPO | Caso 2a - Montagne a 1 cella dal bordo sinistro | FAIL (0/4 arr.) | **FAIL (0/4 arr.)** | 98 -> 98 | 0 |
| MAPPO | Caso 2b - Montagne a 1 cella dal bordo superiore | FAIL (0/4 arr.) | **FAIL (0/4 arr.)** | 0 -> 0 | 0 |
| MAPPO | Caso 2c - Passaggio di 1 cella lungo il bordo destro | FAIL (2/4 arr.) | **FAIL (2/4 arr.)** | 0 -> 0 | 0 |
| PPO | Caso 1a - Contesa della stessa casella ai lati dell'hangar (2 droni) | FAIL (2/4 arr.) | **OK (7 step)** | 100 -> 0 | 1 |
| PPO | Caso 1b - Contesa ai lati dell'hangar con 4 droni | FAIL (3/4 arr.) | **FAIL (3/4 arr.)** | 0 -> 0 | 0 |
| PPO | Caso 2a - Montagne a 1 cella dal bordo sinistro | FAIL (2/4 arr.) | **FAIL (2/4 arr.)** | 0 -> 0 | 0 |
| PPO | Caso 2b - Montagne a 1 cella dal bordo superiore | FAIL (2/4 arr.) | **FAIL (2/4 arr.)** | 0 -> 0 | 0 |
| PPO | Caso 2c - Passaggio di 1 cella lungo il bordo destro | FAIL (2/4 arr.) | **FAIL (2/4 arr.)** | 0 -> 0 | 0 |

## Statistiche su frequenza e cause dei fallimenti (4 droni, 100 episodi/seed)

### Risultati MAPPO - SENZA PRECEDENZA (standard) (300 episodi sui semi `[42, 123, 999]`)
- Episodi completati: 64/300 (21.3%)
- Episodi falliti: 236/300 (78.7%)
- Scontri di vertice totali: 7444 | Precedenze attivate: 0 (in 0/300 episodi)
- Droni non arrivati (567 totali, media 2.40 per episodio fallito):
  - Rimasti bloccati nella stessa cella: 450/567 (79.4%)
  - In movimento continuo senza progredire: 117/567 (20.6%)

| Caso analizzato | Almeno una volta nell'episodio | Fino a fine episodio |
|:---|:---:|:---:|
| Contesa casella ai lati dell'hangar | 30/236 (12.7%) | 22/236 (9.3%) |
| Spazio di 1 cella tra montagna e bordo | 42/236 (17.8%) | 29/236 (12.3%) |

### Risultati MAPPO - CON PRECEDENZA (distanza hangar) (300 episodi sui semi `[42, 123, 999]`)
- Episodi completati: 81/300 (27.0%)
- Episodi falliti: 219/300 (73.0%)
- Scontri di vertice totali: 3680 | Precedenze attivate: 85 (in 69/300 episodi)
- Droni non arrivati (507 totali, media 2.32 per episodio fallito):
  - Rimasti bloccati nella stessa cella: 394/507 (77.7%)
  - In movimento continuo senza progredire: 113/507 (22.3%)

| Caso analizzato | Almeno una volta nell'episodio | Fino a fine episodio |
|:---|:---:|:---:|
| Contesa casella ai lati dell'hangar | 13/219 (5.9%) | 10/219 (4.6%) |
| Spazio di 1 cella tra montagna e bordo | 39/219 (17.8%) | 27/219 (12.3%) |

#### Confronto diretto MAPPO (Senza vs Con Precedenza)

| Metrica | Senza Precedenza | Con Precedenza | Differenza |
|:---|:---:|:---:|:---:|
| Episodi completati | 64/300 (21.3%) | 81/300 (27.0%) | +17 |
| Scontri di vertice | 7444 | 3680 | -3764 |
| Interventi regola di precedenza | 0 | 85 (in 69 ep.) | +85 |
| Contesa lati hangar (persistente) | 22 | 10 | -12 |

- Episodi falliti sbloccati dalla precedenza (18): `[(42, 1, 13, 1), (42, 7, 13, 1), (42, 8, 13, 1), (42, 21, 14, 1), (42, 47, 11, 1), (42, 59, 15, 1), (42, 68, 20, 1), (42, 85, 12, 1), (123, 1, 7, 1), (123, 24, 10, 1), (123, 87, 10, 1), (999, 4, 7, 1), (999, 16, 13, 1), (999, 53, 13, 1), (999, 62, 11, 2), (999, 69, 10, 1), (999, 72, 7, 1), (999, 79, 7, 1)]`

### Risultati PPO - SENZA PRECEDENZA (standard) (300 episodi sui semi `[42, 123, 999]`)
- Episodi completati: 141/300 (47.0%)
- Episodi falliti: 159/300 (53.0%)
- Scontri di vertice totali: 6002 | Precedenze attivate: 0 (in 0/300 episodi)
- Droni non arrivati (305 totali, media 1.92 per episodio fallito):
  - Rimasti bloccati nella stessa cella: 265/305 (86.9%)
  - In movimento continuo senza progredire: 40/305 (13.1%)

| Caso analizzato | Almeno una volta nell'episodio | Fino a fine episodio |
|:---|:---:|:---:|
| Contesa casella ai lati dell'hangar | 16/159 (10.1%) | 15/159 (9.4%) |
| Spazio di 1 cella tra montagna e bordo | 38/159 (23.9%) | 37/159 (23.3%) |

### Risultati PPO - CON PRECEDENZA (distanza hangar) (300 episodi sui semi `[42, 123, 999]`)
- Episodi completati: 161/300 (53.7%)
- Episodi falliti: 139/300 (46.3%)
- Scontri di vertice totali: 2431 | Precedenze attivate: 43 (in 40/300 episodi)
- Droni non arrivati (231 totali, media 1.66 per episodio fallito):
  - Rimasti bloccati nella stessa cella: 191/231 (82.7%)
  - In movimento continuo senza progredire: 40/231 (17.3%)

| Caso analizzato | Almeno una volta nell'episodio | Fino a fine episodio |
|:---|:---:|:---:|
| Contesa casella ai lati dell'hangar | 4/139 (2.9%) | 3/139 (2.2%) |
| Spazio di 1 cella tra montagna e bordo | 37/139 (26.6%) | 37/139 (26.6%) |

#### Confronto diretto PPO (Senza vs Con Precedenza)

| Metrica | Senza Precedenza | Con Precedenza | Differenza |
|:---|:---:|:---:|:---:|
| Episodi completati | 141/300 (47.0%) | 161/300 (53.7%) | +20 |
| Scontri di vertice | 6002 | 2431 | -3571 |
| Interventi regola di precedenza | 0 | 43 (in 40 ep.) | +43 |
| Contesa lati hangar (persistente) | 15 | 3 | -12 |

- Episodi falliti sbloccati dalla precedenza (20): `[(42, 20, 10, 1), (42, 28, 11, 1), (42, 42, 14, 1), (42, 98, 9, 1), (42, 99, 10, 1), (123, 1, 7, 1), (123, 15, 17, 1), (123, 18, 6, 1), (123, 26, 13, 2), (123, 33, 8, 1), (123, 44, 11, 1), (123, 86, 9, 1), (123, 89, 9, 1), (999, 15, 10, 1), (999, 16, 12, 2), (999, 46, 10, 1), (999, 51, 7, 1), (999, 67, 7, 1), (999, 90, 10, 1), (999, 91, 12, 1)]`

### Risultati su 300 episodi per algoritmo (semi `42, 123, 999`)

| Metrica | MAPPO (Senza Precedenza) | MAPPO (Con Precedenza) | $\Delta$ MAPPO | PPO (Senza Precedenza) | PPO (Con Precedenza) | $\Delta$ PPO |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Episodi completati** | 64 / 300 (21.3%) | **81 / 300 (27.0%)** | **+17 (+5.7%)** | 141 / 300 (47.0%) | **161 / 300 (53.7%)** | **+20 (+6.7%)** |
| **Scontri di vertice totali** | 7.444 | **3.680** | **-3.764 (-50.6%)** | 6.002 | **2.431** | **-3.571 (-59.5%)** |
| **Interventi regola precedenza** | 0 | **85** (in 69 ep.) | +85 | 0 | **43** (in 40 ep.) | +43 |
| **Contesa lati hangar (persistente)** | 22 / 236 (9.3%) | **10 / 219 (4.6%)** | **-54.5%** | 15 / 159 (9.4%) | **3 / 139 (2.2%)** | **-80.0%** |
| **Varco 1 cella sul bordo (persistente)** | 29 / 236 (12.3%) | **27 / 219 (12.3%)** | Invariato | 37 / 159 (23.3%) | **37 / 139 (26.6%)** | Invariato |

