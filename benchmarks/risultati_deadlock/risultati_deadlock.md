# Risultati test deadlock: Regola di Precedenza + Action Masking + Anti-Livelock (4 droni)

Meccanismi testati in esecuzione (senza riaddestramento):
1. **Regola di precedenza**: su cella libera contesa passa il drone che si avvicina all'hangar (a parità, indice minore `D0 > D1 > D2 > D3`).
2. **Action Masking sulle mosse invalide**: mascheramento ($-\infty$) delle direzioni che portano fuori griglia, dentro una montagna o a restare fermi volontariamente.
3. **Anti-Livelock / Loop-Breaking**: mascheramento del ritorno immediato alla cella del passo $t-1$ ($A \leftrightarrow B$) e preferenza per le celle meno visitate in caso di cicli.

## Scenari con posizionamento specifico (seed modello: 42)

### [MAPPO - seed 42 - SENZA PRECEDENZA (STANDARD)] Caso 1a - Contesa della stessa casella ai lati dell'hangar (2 droni)
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

- Esito: fallimento per timeout a 100 step (reward: -1.0, droni arrivati: 3/4, precedenze: 0, action-mask: 0, anti-loop: 0)
- Comportamento: i droni continuano a muoversi senza progredire
  - Drone D1: si muove avanti e indietro tra le celle [(5, 9), (5, 8)]

### [MAPPO - seed 42 - CON PRECEDENZA + MASK + ANTI-LOOP] Caso 1a - Contesa della stessa casella ai lati dell'hangar (2 droni)
Hangar in (4,8). I droni D0 e D2 sono gia arrivati, mentre D1 in (5,7) e D3 in (4,6) cercano entrambi di passare per la casella (4,7) sopra l'hangar.
- Hangar: `(4, 8)` | Montagne: `[(1, 1), (8, 1), (1, 4), (8, 4)]` | Droni: `[(4, 8), (5, 7), (4, 8), (4, 6)]`

```text
Step   1: pos=[(4, 8), (5, 7), (4, 8), (4, 6)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(4, 8), (5, 8), (4, 8), (4, 7)] (droni mossi: [1, 3])
Step   2: pos=[(4, 8), (5, 8), (4, 8), (4, 7)] | azioni=[D0:arrivato, D1:Sinistra, D2:arrivato, D3:Giu]
          -> nuove pos=[(4, 8), (4, 8), (4, 8), (4, 8)] (anti-loop D1(5, 8): Giu->Sinistra)
```

- Esito: completato in 2 step (reward: 198.0, precedenze: 0, action-mask: 0, anti-loop: 1)

### [MAPPO - seed 42 - SENZA PRECEDENZA (STANDARD)] Caso 1b - Contesa ai lati dell'hangar con 4 droni
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

- Esito: fallimento per timeout a 100 step (reward: 165.0, droni arrivati: 3/4, precedenze: 0, action-mask: 0, anti-loop: 0)
- Comportamento: i droni continuano a muoversi senza progredire
  - Drone D0: si muove avanti e indietro tra le celle [(4, 5), (4, 4)]

### [MAPPO - seed 42 - CON PRECEDENZA + MASK + ANTI-LOOP] Caso 1b - Contesa ai lati dell'hangar con 4 droni
Hangar in (5,5) con montagne sopra (5,4) e sotto (5,6). D0(3,5) e D1(4,4) puntano al lato sinistro (4,5), mentre D2(7,5) e D3(6,6) puntano al lato destro (6,5).
- Hangar: `(5, 5)` | Montagne: `[(5, 4), (5, 6), (1, 1), (8, 8)]` | Droni: `[(3, 5), (4, 4), (7, 5), (6, 6)]`

```text
Step   1: pos=[(3, 5), (4, 4), (7, 5), (6, 6)] | azioni=[D0:Giu, D1:Giu, D2:Sinistra, D3:Su]
          -> nuove pos=[(3, 6), (4, 5), (6, 5), (6, 6)] (mask D3(6, 6): Sinistra->Su | precedenza su (6, 5): passa D2(7, 5) (dist=2), attende D3(6, 6) (dist=2))
Step   2: pos=[(3, 6), (4, 5), (6, 5), (6, 6)] | azioni=[D0:Destra, D1:Destra, D2:Sinistra, D3:Su]
          -> nuove pos=[(4, 6), (5, 5), (5, 5), (6, 5)] (anti-loop D1(4, 5): Giu->Destra)
Step   3: pos=[(4, 6), (5, 5), (5, 5), (6, 5)] | azioni=[D0:Su, D1:arrivato, D2:arrivato, D3:Sinistra]
          -> nuove pos=[(4, 5), (5, 5), (5, 5), (5, 5)] (anti-loop D3(6, 5): Giu->Sinistra)
Step   4: pos=[(4, 5), (5, 5), (5, 5), (5, 5)] | azioni=[D0:Destra, D1:arrivato, D2:arrivato, D3:arrivato]
          -> nuove pos=[(5, 5), (5, 5), (5, 5), (5, 5)] (anti-loop D0(4, 5): Su->Destra)
```

- Esito: completato in 4 step (reward: 393.0, precedenze: 1, action-mask: 1, anti-loop: 3)

### [MAPPO - seed 42 - SENZA PRECEDENZA (STANDARD)] Caso 2a - Montagne a 1 cella dal bordo sinistro
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

- Esito: fallimento per timeout a 100 step (reward: -5340.0, droni arrivati: 0/4, precedenze: 0, action-mask: 0, anti-loop: 0)
- Comportamento: i droni rimangono effettivamente bloccati
  - Drone D0: resta fermo nella cella (0, 6)
  - Drone D1: resta fermo nella cella (1, 4)
  - Drone D2: resta fermo nella cella (0, 5)
  - Drone D3: resta fermo nella cella (2, 4)

### [MAPPO - seed 42 - CON PRECEDENZA + MASK + ANTI-LOOP] Caso 2a - Montagne a 1 cella dal bordo sinistro
Montagne in (1,5), (2,5), (3,5), (4,5) che lasciano solo la cella (0,5) libera sul bordo sinistro. Hangar in (0,7) e droni in (0,4), (1,4), (0,3) e (2,4) che devono passare da (0,5).
- Hangar: `(0, 7)` | Montagne: `[(1, 5), (2, 5), (3, 5), (4, 5)]` | Droni: `[(0, 4), (1, 4), (0, 3), (2, 4)]`

```text
Step   1: pos=[(0, 4), (1, 4), (0, 3), (2, 4)] | azioni=[D0:Giu, D1:Destra, D2:Giu, D3:Destra]
          -> nuove pos=[(0, 5), (2, 4), (0, 4), (3, 4)] (mask D1(1, 4): Giu->Destra | mask D3(2, 4): Giu->Destra)
Step   2: pos=[(0, 5), (2, 4), (0, 4), (3, 4)] | azioni=[D0:Giu, D1:Destra, D2:Giu, D3:Destra]
          -> nuove pos=[(0, 6), (3, 4), (0, 5), (4, 4)] (mask D1(2, 4): Giu->Sinistra | mask D3(3, 4): Giu->Sinistra | anti-loop D1(2, 4): Sinistra->Destra | anti-loop D3(3, 4): Sinistra->Destra)
Step   3: pos=[(0, 6), (3, 4), (0, 5), (4, 4)] | azioni=[D0:Giu, D1:Destra, D2:Giu, D3:Destra]
          -> nuove pos=[(0, 7), (4, 4), (0, 6), (5, 4)] (mask D0(0, 6): Sinistra->Giu | mask D1(3, 4): Giu->Sinistra | mask D3(4, 4): Giu->Sinistra | anti-loop D1(3, 4): Sinistra->Destra | anti-loop D3(4, 4): Sinistra->Destra)
Step   4: pos=[(0, 7), (4, 4), (0, 6), (5, 4)] | azioni=[D0:arrivato, D1:Destra, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 7), (5, 4), (0, 7), (5, 5)] (mask D1(4, 4): Giu->Sinistra | anti-loop D1(4, 4): Sinistra->Destra)
Step   5: pos=[(0, 7), (5, 4), (0, 7), (5, 5)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(0, 7), (5, 5), (0, 7), (5, 6)] (anti-loop D1(5, 4): Sinistra->Giu)
Step   6: pos=[(0, 7), (5, 5), (0, 7), (5, 6)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Sinistra]
          -> nuove pos=[(0, 7), (5, 6), (0, 7), (4, 6)] (mask D1(5, 5): Sinistra->Giu)
Step   7: pos=[(0, 7), (5, 6), (0, 7), (4, 6)] | azioni=[D0:arrivato, D1:Sinistra, D2:arrivato, D3:Sinistra]
          -> nuove pos=[(0, 7), (4, 6), (0, 7), (3, 6)] (droni mossi: [1, 3])
Step   8: pos=[(0, 7), (4, 6), (0, 7), (3, 6)] | azioni=[D0:arrivato, D1:Sinistra, D2:arrivato, D3:Sinistra]
          -> nuove pos=[(0, 7), (3, 6), (0, 7), (2, 6)] (droni mossi: [1, 3])
  ... (dal passo 9 al 9 si ripete lo stesso comportamento) ...
Step  10: pos=[(0, 7), (2, 6), (0, 7), (1, 6)] | azioni=[D0:arrivato, D1:Sinistra, D2:arrivato, D3:Giu]
          -> nuove pos=[(0, 7), (1, 6), (0, 7), (1, 7)] (droni mossi: [1, 3])
Step  11: pos=[(0, 7), (1, 6), (0, 7), (1, 7)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Sinistra]
          -> nuove pos=[(0, 7), (1, 7), (0, 7), (0, 7)] (droni mossi: [1, 3])
Step  12: pos=[(0, 7), (1, 7), (0, 7), (0, 7)] | azioni=[D0:arrivato, D1:Sinistra, D2:arrivato, D3:arrivato]
          -> nuove pos=[(0, 7), (0, 7), (0, 7), (0, 7)] (droni mossi: [1])
```

- Esito: completato in 12 step (reward: 374.0, precedenze: 0, action-mask: 9, anti-loop: 6)

### [MAPPO - seed 42 - SENZA PRECEDENZA (STANDARD)] Caso 2b - Montagne a 1 cella dal bordo superiore
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

- Esito: fallimento per timeout a 100 step (reward: -400.0, droni arrivati: 0/4, precedenze: 0, action-mask: 0, anti-loop: 0)
- Comportamento: i droni rimangono effettivamente bloccati
  - Drone D0: resta fermo nella cella (4, 0)
  - Drone D1: resta fermo nella cella (4, 1)
  - Drone D2: resta fermo nella cella (3, 0)
  - Drone D3: resta fermo nella cella (4, 2)

### [MAPPO - seed 42 - CON PRECEDENZA + MASK + ANTI-LOOP] Caso 2b - Montagne a 1 cella dal bordo superiore
Montagne in (5,1), (5,2), (5,3), (5,4) che lasciano solo la cella (5,0) libera sul bordo in alto. Hangar in (7,0) e droni in (4,0), (4,1), (3,0), (4,2) che devono passare da (5,0).
- Hangar: `(7, 0)` | Montagne: `[(5, 1), (5, 2), (5, 3), (5, 4)]` | Droni: `[(4, 0), (4, 1), (3, 0), (4, 2)]`

```text
Step   1: pos=[(4, 0), (4, 1), (3, 0), (4, 2)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Su]
          -> nuove pos=[(4, 0), (4, 1), (3, 1), (4, 2)] (mask D0(4, 0): Fermo->Giu | mask D1(4, 1): Fermo->Giu | mask D2(3, 0): Fermo->Giu | mask D3(4, 2): Fermo->Su | scontro tra D0(4, 0) e D1(4, 1) sulla cella (4, 1) | scambio di posizione bloccato tra D1(4, 1) e D3(4, 2))
Step   2: pos=[(4, 0), (4, 1), (3, 1), (4, 2)] | azioni=[D0:Destra, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(5, 0), (4, 2), (3, 2), (4, 3)] (mask D0(4, 0): Fermo->Destra | mask D1(4, 1): Fermo->Giu | mask D2(3, 1): Fermo->Giu | mask D3(4, 2): Fermo->Giu)
Step   3: pos=[(5, 0), (4, 2), (3, 2), (4, 3)] | azioni=[D0:Destra, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(6, 0), (4, 3), (3, 3), (4, 4)] (mask D0(5, 0): Fermo->Destra | mask D1(4, 2): Fermo->Su | mask D2(3, 2): Fermo->Su | mask D3(4, 3): Fermo->Su | anti-loop D1(4, 2): Su->Giu | anti-loop D2(3, 2): Su->Giu | anti-loop D3(4, 3): Su->Giu)
Step   4: pos=[(6, 0), (4, 3), (3, 3), (4, 4)] | azioni=[D0:Destra, D1:Giu, D2:Destra, D3:Giu]
          -> nuove pos=[(7, 0), (4, 4), (4, 3), (4, 5)] (mask D0(6, 0): Fermo->Giu | mask D1(4, 3): Fermo->Su | mask D2(3, 3): Fermo->Su | mask D3(4, 4): Fermo->Su | anti-loop D0(6, 0): Giu->Destra | anti-loop D1(4, 3): Su->Giu | anti-loop D2(3, 3): Su->Destra | anti-loop D3(4, 4): Su->Giu)
Step   5: pos=[(7, 0), (4, 4), (4, 3), (4, 5)] | azioni=[D0:arrivato, D1:Giu, D2:Su, D3:Destra]
          -> nuove pos=[(7, 0), (4, 5), (4, 2), (5, 5)] (mask D1(4, 4): Fermo->Su | mask D2(4, 3): Fermo->Su | mask D3(4, 5): Fermo->Su | anti-loop D1(4, 4): Su->Giu | anti-loop D3(4, 5): Su->Destra)
Step   6: pos=[(7, 0), (4, 5), (4, 2), (5, 5)] | azioni=[D0:arrivato, D1:Destra, D2:Su, D3:Destra]
          -> nuove pos=[(7, 0), (5, 5), (4, 1), (6, 5)] (mask D1(4, 5): Fermo->Su | mask D2(4, 2): Fermo->Giu | mask D3(5, 5): Fermo->Destra | anti-loop D1(4, 5): Su->Destra | anti-loop D2(4, 2): Giu->Su)
Step   7: pos=[(7, 0), (5, 5), (4, 1), (6, 5)] | azioni=[D0:arrivato, D1:Destra, D2:Su, D3:Su]
          -> nuove pos=[(7, 0), (6, 5), (4, 0), (6, 4)] (mask D1(5, 5): Fermo->Destra | mask D2(4, 1): Fermo->Giu | mask D3(6, 5): Fermo->Su | anti-loop D2(4, 1): Giu->Su)
Step   8: pos=[(7, 0), (6, 5), (4, 0), (6, 4)] | azioni=[D0:arrivato, D1:Su, D2:Destra, D3:Su]
          -> nuove pos=[(7, 0), (6, 4), (5, 0), (6, 3)] (mask D1(6, 5): Fermo->Su | mask D2(4, 0): Fermo->Giu | mask D3(6, 4): Fermo->Su | anti-loop D2(4, 0): Giu->Destra)
  ... (dal passo 9 al 10 si ripete lo stesso comportamento) ...
Step  11: pos=[(7, 0), (6, 2), (7, 0), (6, 1)] | azioni=[D0:arrivato, D1:Su, D2:arrivato, D3:Su]
          -> nuove pos=[(7, 0), (6, 1), (7, 0), (6, 0)] (mask D1(6, 2): Fermo->Giu | mask D3(6, 1): Fermo->Giu | anti-loop D1(6, 2): Giu->Su | anti-loop D3(6, 1): Giu->Su)
Step  12: pos=[(7, 0), (6, 1), (7, 0), (6, 0)] | azioni=[D0:arrivato, D1:Su, D2:arrivato, D3:Destra]
          -> nuove pos=[(7, 0), (6, 0), (7, 0), (7, 0)] (mask D1(6, 1): Fermo->Giu | mask D3(6, 0): Fermo->Giu | anti-loop D1(6, 1): Giu->Su | anti-loop D3(6, 0): Giu->Destra)
Step  13: pos=[(7, 0), (6, 0), (7, 0), (7, 0)] | azioni=[D0:arrivato, D1:Destra, D2:arrivato, D3:arrivato]
          -> nuove pos=[(7, 0), (7, 0), (7, 0), (7, 0)] (mask D1(6, 0): Fermo->Giu | anti-loop D1(6, 0): Giu->Destra)
```

- Esito: completato in 13 step (reward: 325.0, precedenze: 0, action-mask: 39, anti-loop: 20)

### [MAPPO - seed 42 - SENZA PRECEDENZA (STANDARD)] Caso 2c - Passaggio di 1 cella lungo il bordo destro
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

- Esito: fallimento per timeout a 100 step (reward: -1967.0, droni arrivati: 2/4, precedenze: 0, action-mask: 0, anti-loop: 0)
- Comportamento: i droni rimangono effettivamente bloccati
  - Drone D1: resta fermo nella cella (8, 4)
  - Drone D3: resta fermo nella cella (7, 6)

### [MAPPO - seed 42 - CON PRECEDENZA + MASK + ANTI-LOOP] Caso 2c - Passaggio di 1 cella lungo il bordo destro
Montagne in (8,5), (8,6), (8,7), (7,7) che lasciano un passaggio di 1 cella sul bordo destro per arrivare all'hangar in (9,8). Droni in partenza da (9,4), (8,4), (9,3), (7,4).
- Hangar: `(9, 8)` | Montagne: `[(8, 5), (8, 6), (8, 7), (7, 7)]` | Droni: `[(9, 4), (8, 4), (9, 3), (7, 4)]`

```text
Step   1: pos=[(9, 4), (8, 4), (9, 3), (7, 4)] | azioni=[D0:Giu, D1:Destra, D2:Giu, D3:Giu]
          -> nuove pos=[(9, 5), (9, 4), (9, 3), (7, 5)] (mask D1(8, 4): Fermo->Destra | mask D3(7, 4): Fermo->Giu | precedenza su (9, 4): passa D1(8, 4) (dist=5), attende D2(9, 3) (dist=5))
Step   2: pos=[(9, 5), (9, 4), (9, 3), (7, 5)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(9, 6), (9, 5), (9, 4), (7, 6)] (mask D3(7, 5): Fermo->Giu)
Step   3: pos=[(9, 6), (9, 5), (9, 4), (7, 6)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Sinistra]
          -> nuove pos=[(9, 7), (9, 6), (9, 5), (6, 6)] (mask D3(7, 6): Giu->Su | anti-loop D3(7, 6): Su->Sinistra)
Step   4: pos=[(9, 7), (9, 6), (9, 5), (6, 6)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(9, 8), (9, 7), (9, 6), (6, 7)] (droni mossi: [0, 1, 2, 3])
Step   5: pos=[(9, 8), (9, 7), (9, 6), (6, 7)] | azioni=[D0:arrivato, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(9, 8), (9, 8), (9, 7), (6, 8)] (mask D3(6, 7): Fermo->Giu)
Step   6: pos=[(9, 8), (9, 8), (9, 7), (6, 8)] | azioni=[D0:arrivato, D1:arrivato, D2:Giu, D3:Destra]
          -> nuove pos=[(9, 8), (9, 8), (9, 8), (7, 8)] (droni mossi: [2, 3])
Step   7: pos=[(9, 8), (9, 8), (9, 8), (7, 8)] | azioni=[D0:arrivato, D1:arrivato, D2:arrivato, D3:Destra]
          -> nuove pos=[(9, 8), (9, 8), (9, 8), (8, 8)] (droni mossi: [3])
Step   8: pos=[(9, 8), (9, 8), (9, 8), (8, 8)] | azioni=[D0:arrivato, D1:arrivato, D2:arrivato, D3:Destra]
          -> nuove pos=[(9, 8), (9, 8), (9, 8), (9, 8)] (mask D3(8, 8): Fermo->Giu | anti-loop D3(8, 8): Giu->Destra)
```

- Esito: completato in 8 step (reward: 381.0, precedenze: 1, action-mask: 6, anti-loop: 2)

### [PPO - seed 42 - SENZA PRECEDENZA (STANDARD)] Caso 1a - Contesa della stessa casella ai lati dell'hangar (2 droni)
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

- Esito: fallimento per timeout a 100 step (reward: -2200.0, droni arrivati: 2/4, precedenze: 0, action-mask: 0, anti-loop: 0)
- Comportamento: i droni rimangono effettivamente bloccati
  - Drone D1: resta fermo nella cella (5, 7)
  - Drone D3: resta fermo nella cella (4, 6)

### [PPO - seed 42 - CON PRECEDENZA + MASK + ANTI-LOOP] Caso 1a - Contesa della stessa casella ai lati dell'hangar (2 droni)
Hangar in (4,8). I droni D0 e D2 sono gia arrivati, mentre D1 in (5,7) e D3 in (4,6) cercano entrambi di passare per la casella (4,7) sopra l'hangar.
- Hangar: `(4, 8)` | Montagne: `[(1, 1), (8, 1), (1, 4), (8, 4)]` | Droni: `[(4, 8), (5, 7), (4, 8), (4, 6)]`

```text
Step   1: pos=[(4, 8), (5, 7), (4, 8), (4, 6)] | azioni=[D0:arrivato, D1:Sinistra, D2:arrivato, D3:Giu]
          -> nuove pos=[(4, 8), (4, 7), (4, 8), (4, 6)] (precedenza su (4, 7): passa D1(5, 7) (dist=2), attende D3(4, 6) (dist=2))
Step   2: pos=[(4, 8), (4, 7), (4, 8), (4, 6)] | azioni=[D0:arrivato, D1:Giu, D2:arrivato, D3:Giu]
          -> nuove pos=[(4, 8), (4, 8), (4, 8), (4, 7)] (anti-loop D1(4, 7): Sinistra->Giu)
Step   3: pos=[(4, 8), (4, 8), (4, 8), (4, 7)] | azioni=[D0:arrivato, D1:arrivato, D2:arrivato, D3:Giu]
          -> nuove pos=[(4, 8), (4, 8), (4, 8), (4, 8)] (anti-loop D3(4, 7): Sinistra->Giu)
```

- Esito: completato in 3 step (reward: 197.0, precedenze: 1, action-mask: 0, anti-loop: 2)

### [PPO - seed 42 - SENZA PRECEDENZA (STANDARD)] Caso 1b - Contesa ai lati dell'hangar con 4 droni
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

- Esito: fallimento per timeout a 100 step (reward: -814.0, droni arrivati: 3/4, precedenze: 0, action-mask: 0, anti-loop: 0)
- Comportamento: i droni rimangono effettivamente bloccati
  - Drone D3: resta fermo nella cella (6, 6)

### [PPO - seed 42 - CON PRECEDENZA + MASK + ANTI-LOOP] Caso 1b - Contesa ai lati dell'hangar con 4 droni
Hangar in (5,5) con montagne sopra (5,4) e sotto (5,6). D0(3,5) e D1(4,4) puntano al lato sinistro (4,5), mentre D2(7,5) e D3(6,6) puntano al lato destro (6,5).
- Hangar: `(5, 5)` | Montagne: `[(5, 4), (5, 6), (1, 1), (8, 8)]` | Droni: `[(3, 5), (4, 4), (7, 5), (6, 6)]`

```text
Step   1: pos=[(3, 5), (4, 4), (7, 5), (6, 6)] | azioni=[D0:Destra, D1:Giu, D2:Sinistra, D3:Su]
          -> nuove pos=[(4, 5), (4, 4), (6, 5), (6, 6)] (mask D1(4, 4): Destra->Giu | mask D3(6, 6): Sinistra->Su | precedenza su (4, 5): passa D0(3, 5) (dist=2), attende D1(4, 4) (dist=2) | precedenza su (6, 5): passa D2(7, 5) (dist=2), attende D3(6, 6) (dist=2))
Step   2: pos=[(4, 5), (4, 4), (6, 5), (6, 6)] | azioni=[D0:Destra, D1:Giu, D2:Sinistra, D3:Su]
          -> nuove pos=[(5, 5), (4, 5), (5, 5), (6, 5)] (mask D3(6, 6): Sinistra->Su)
Step   3: pos=[(5, 5), (4, 5), (5, 5), (6, 5)] | azioni=[D0:arrivato, D1:Destra, D2:arrivato, D3:Sinistra]
          -> nuove pos=[(5, 5), (5, 5), (5, 5), (5, 5)] (droni mossi: [1, 3])
```

- Esito: completato in 3 step (reward: 394.0, precedenze: 2, action-mask: 3, anti-loop: 0)

### [PPO - seed 42 - SENZA PRECEDENZA (STANDARD)] Caso 2a - Montagne a 1 cella dal bordo sinistro
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

- Esito: fallimento per timeout a 100 step (reward: -2005.0, droni arrivati: 2/4, precedenze: 0, action-mask: 0, anti-loop: 0)
- Comportamento: i droni rimangono effettivamente bloccati
  - Drone D1: resta fermo nella cella (1, 4)
  - Drone D3: resta fermo nella cella (2, 4)

### [PPO - seed 42 - CON PRECEDENZA + MASK + ANTI-LOOP] Caso 2a - Montagne a 1 cella dal bordo sinistro
Montagne in (1,5), (2,5), (3,5), (4,5) che lasciano solo la cella (0,5) libera sul bordo sinistro. Hangar in (0,7) e droni in (0,4), (1,4), (0,3) e (2,4) che devono passare da (0,5).
- Hangar: `(0, 7)` | Montagne: `[(1, 5), (2, 5), (3, 5), (4, 5)]` | Droni: `[(0, 4), (1, 4), (0, 3), (2, 4)]`

```text
Step   1: pos=[(0, 4), (1, 4), (0, 3), (2, 4)] | azioni=[D0:Giu, D1:Sinistra, D2:Giu, D3:Sinistra]
          -> nuove pos=[(0, 5), (0, 4), (0, 3), (1, 4)] (mask D1(1, 4): Giu->Sinistra | mask D3(2, 4): Giu->Sinistra | precedenza su (0, 4): passa D1(1, 4) (dist=4), attende D2(0, 3) (dist=4))
Step   2: pos=[(0, 5), (0, 4), (0, 3), (1, 4)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Sinistra]
          -> nuove pos=[(0, 6), (0, 5), (0, 4), (1, 4)] (mask D3(1, 4): Giu->Sinistra | precedenza su (0, 4): passa D2(0, 3) (dist=4), attende D3(1, 4) (dist=4))
Step   3: pos=[(0, 6), (0, 5), (0, 4), (1, 4)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Sinistra]
          -> nuove pos=[(0, 7), (0, 6), (0, 5), (0, 4)] (mask D3(1, 4): Giu->Sinistra)
Step   4: pos=[(0, 7), (0, 6), (0, 5), (0, 4)] | azioni=[D0:arrivato, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 7), (0, 7), (0, 6), (0, 5)] (droni mossi: [1, 2, 3])
Step   5: pos=[(0, 7), (0, 7), (0, 6), (0, 5)] | azioni=[D0:arrivato, D1:arrivato, D2:Giu, D3:Giu]
          -> nuove pos=[(0, 7), (0, 7), (0, 7), (0, 6)] (droni mossi: [2, 3])
Step   6: pos=[(0, 7), (0, 7), (0, 7), (0, 6)] | azioni=[D0:arrivato, D1:arrivato, D2:arrivato, D3:Giu]
          -> nuove pos=[(0, 7), (0, 7), (0, 7), (0, 7)] (droni mossi: [3])
```

- Esito: completato in 6 step (reward: 386.0, precedenze: 2, action-mask: 4, anti-loop: 0)

### [PPO - seed 42 - SENZA PRECEDENZA (STANDARD)] Caso 2b - Montagne a 1 cella dal bordo superiore
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

- Esito: fallimento per timeout a 100 step (reward: -2005.0, droni arrivati: 2/4, precedenze: 0, action-mask: 0, anti-loop: 0)
- Comportamento: i droni rimangono effettivamente bloccati
  - Drone D1: resta fermo nella cella (4, 1)
  - Drone D3: resta fermo nella cella (4, 2)

### [PPO - seed 42 - CON PRECEDENZA + MASK + ANTI-LOOP] Caso 2b - Montagne a 1 cella dal bordo superiore
Montagne in (5,1), (5,2), (5,3), (5,4) che lasciano solo la cella (5,0) libera sul bordo in alto. Hangar in (7,0) e droni in (4,0), (4,1), (3,0), (4,2) che devono passare da (5,0).
- Hangar: `(7, 0)` | Montagne: `[(5, 1), (5, 2), (5, 3), (5, 4)]` | Droni: `[(4, 0), (4, 1), (3, 0), (4, 2)]`

```text
Step   1: pos=[(4, 0), (4, 1), (3, 0), (4, 2)] | azioni=[D0:Destra, D1:Su, D2:Destra, D3:Su]
          -> nuove pos=[(5, 0), (4, 0), (3, 0), (4, 1)] (mask D1(4, 1): Destra->Su | mask D3(4, 2): Destra->Su | precedenza su (4, 0): passa D1(4, 1) (dist=4), attende D2(3, 0) (dist=4))
Step   2: pos=[(5, 0), (4, 0), (3, 0), (4, 1)] | azioni=[D0:Destra, D1:Destra, D2:Destra, D3:Su]
          -> nuove pos=[(6, 0), (5, 0), (4, 0), (4, 1)] (mask D3(4, 1): Destra->Su | precedenza su (4, 0): passa D2(3, 0) (dist=4), attende D3(4, 1) (dist=4))
Step   3: pos=[(6, 0), (5, 0), (4, 0), (4, 1)] | azioni=[D0:Destra, D1:Destra, D2:Destra, D3:Su]
          -> nuove pos=[(7, 0), (6, 0), (5, 0), (4, 0)] (mask D3(4, 1): Destra->Su)
Step   4: pos=[(7, 0), (6, 0), (5, 0), (4, 0)] | azioni=[D0:arrivato, D1:Destra, D2:Destra, D3:Destra]
          -> nuove pos=[(7, 0), (7, 0), (6, 0), (5, 0)] (droni mossi: [1, 2, 3])
Step   5: pos=[(7, 0), (7, 0), (6, 0), (5, 0)] | azioni=[D0:arrivato, D1:arrivato, D2:Destra, D3:Destra]
          -> nuove pos=[(7, 0), (7, 0), (7, 0), (6, 0)] (droni mossi: [2, 3])
Step   6: pos=[(7, 0), (7, 0), (7, 0), (6, 0)] | azioni=[D0:arrivato, D1:arrivato, D2:arrivato, D3:Destra]
          -> nuove pos=[(7, 0), (7, 0), (7, 0), (7, 0)] (droni mossi: [3])
```

- Esito: completato in 6 step (reward: 386.0, precedenze: 2, action-mask: 4, anti-loop: 0)

### [PPO - seed 42 - SENZA PRECEDENZA (STANDARD)] Caso 2c - Passaggio di 1 cella lungo il bordo destro
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

- Esito: fallimento per timeout a 100 step (reward: -1987.0, droni arrivati: 2/4, precedenze: 0, action-mask: 0, anti-loop: 0)
- Comportamento: i droni rimangono effettivamente bloccati
  - Drone D1: resta fermo nella cella (8, 4)
  - Drone D3: resta fermo nella cella (7, 6)

### [PPO - seed 42 - CON PRECEDENZA + MASK + ANTI-LOOP] Caso 2c - Passaggio di 1 cella lungo il bordo destro
Montagne in (8,5), (8,6), (8,7), (7,7) che lasciano un passaggio di 1 cella sul bordo destro per arrivare all'hangar in (9,8). Droni in partenza da (9,4), (8,4), (9,3), (7,4).
- Hangar: `(9, 8)` | Montagne: `[(8, 5), (8, 6), (8, 7), (7, 7)]` | Droni: `[(9, 4), (8, 4), (9, 3), (7, 4)]`

```text
Step   1: pos=[(9, 4), (8, 4), (9, 3), (7, 4)] | azioni=[D0:Giu, D1:Destra, D2:Giu, D3:Giu]
          -> nuove pos=[(9, 5), (9, 4), (9, 3), (7, 5)] (mask D1(8, 4): Giu->Destra | precedenza su (9, 4): passa D1(8, 4) (dist=5), attende D2(9, 3) (dist=5))
Step   2: pos=[(9, 5), (9, 4), (9, 3), (7, 5)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(9, 6), (9, 5), (9, 4), (7, 6)] (droni mossi: [0, 1, 2, 3])
Step   3: pos=[(9, 6), (9, 5), (9, 4), (7, 6)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Sinistra]
          -> nuove pos=[(9, 7), (9, 6), (9, 5), (6, 6)] (mask D3(7, 6): Giu->Sinistra)
Step   4: pos=[(9, 7), (9, 6), (9, 5), (6, 6)] | azioni=[D0:Giu, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(9, 8), (9, 7), (9, 6), (6, 7)] (droni mossi: [0, 1, 2, 3])
Step   5: pos=[(9, 8), (9, 7), (9, 6), (6, 7)] | azioni=[D0:arrivato, D1:Giu, D2:Giu, D3:Giu]
          -> nuove pos=[(9, 8), (9, 8), (9, 7), (6, 8)] (mask D3(6, 7): Destra->Giu)
Step   6: pos=[(9, 8), (9, 8), (9, 7), (6, 8)] | azioni=[D0:arrivato, D1:arrivato, D2:Giu, D3:Destra]
          -> nuove pos=[(9, 8), (9, 8), (9, 8), (7, 8)] (droni mossi: [2, 3])
Step   7: pos=[(9, 8), (9, 8), (9, 8), (7, 8)] | azioni=[D0:arrivato, D1:arrivato, D2:arrivato, D3:Destra]
          -> nuove pos=[(9, 8), (9, 8), (9, 8), (8, 8)] (droni mossi: [3])
Step   8: pos=[(9, 8), (9, 8), (9, 8), (8, 8)] | azioni=[D0:arrivato, D1:arrivato, D2:arrivato, D3:Destra]
          -> nuove pos=[(9, 8), (9, 8), (9, 8), (9, 8)] (droni mossi: [3])
```

- Esito: completato in 8 step (reward: 381.0, precedenze: 1, action-mask: 3, anti-loop: 0)

### Riepilogo confronto scenari fissi (Standard vs Precedenza + Masking + Anti-Livelock)

| Algoritmo | Scenario | Standard | Con Precedenza + Mask + Anti-Loop | Scontri Vertice (Prima -> Dopo) | Precedenze | Action Mask | Anti-Loop |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| MAPPO | Caso 1a - Contesa della stessa casella ai lati dell'hangar (2 droni) | FAIL (3/4 arr.) | **OK (2 step)** | 0 -> 0 | 0 | 0 | 1 |
| MAPPO | Caso 1b - Contesa ai lati dell'hangar con 4 droni | FAIL (3/4 arr.) | **OK (4 step)** | 1 -> 0 | 1 | 1 | 3 |
| MAPPO | Caso 2a - Montagne a 1 cella dal bordo sinistro | FAIL (0/4 arr.) | **OK (12 step)** | 98 -> 0 | 0 | 9 | 6 |
| MAPPO | Caso 2b - Montagne a 1 cella dal bordo superiore | FAIL (0/4 arr.) | **OK (13 step)** | 0 -> 1 | 0 | 39 | 20 |
| MAPPO | Caso 2c - Passaggio di 1 cella lungo il bordo destro | FAIL (2/4 arr.) | **OK (8 step)** | 0 -> 0 | 1 | 6 | 2 |
| PPO | Caso 1a - Contesa della stessa casella ai lati dell'hangar (2 droni) | FAIL (2/4 arr.) | **OK (3 step)** | 100 -> 0 | 1 | 0 | 2 |
| PPO | Caso 1b - Contesa ai lati dell'hangar con 4 droni | FAIL (3/4 arr.) | **OK (3 step)** | 0 -> 0 | 2 | 3 | 0 |
| PPO | Caso 2a - Montagne a 1 cella dal bordo sinistro | FAIL (2/4 arr.) | **OK (6 step)** | 0 -> 0 | 2 | 4 | 0 |
| PPO | Caso 2b - Montagne a 1 cella dal bordo superiore | FAIL (2/4 arr.) | **OK (6 step)** | 0 -> 0 | 2 | 4 | 0 |
| PPO | Caso 2c - Passaggio di 1 cella lungo il bordo destro | FAIL (2/4 arr.) | **OK (8 step)** | 0 -> 0 | 1 | 3 | 0 |

## Statistiche su frequenza e cause dei fallimenti (4 droni, 100 episodi/seed)

### Risultati MAPPO - SENZA PRECEDENZA (standard) (300 episodi sui semi `[42, 123, 999]`)
- Episodi completati: 64/300 (21.3%)
- Episodi falliti: 236/300 (78.7%)
- Scontri di vertice totali: 7444 | Precedenze attivate: 0 (in 0/300 ep.) | Action-Masking: 0 | Anti-Livelock: 0
- Droni non arrivati (567 totali, media 2.40 per episodio fallito):
  - Rimasti bloccati nella stessa cella: 450/567 (79.4%)
  - In movimento continuo senza progredire: 117/567 (20.6%)

| Caso analizzato | Almeno una volta nell'episodio | Fino a fine episodio |
|:---|:---:|:---:|
| Contesa casella ai lati dell'hangar | 30/236 (12.7%) | 22/236 (9.3%) |
| Spazio di 1 cella tra montagna e bordo | 42/236 (17.8%) | 29/236 (12.3%) |

### Risultati MAPPO - CON PRECEDENZA + ACTION MASKING + ANTI-LIVELOCK (300 episodi sui semi `[42, 123, 999]`)
- Episodi completati: 297/300 (99.0%)
- Episodi falliti: 3/300 (1.0%)
- Scontri di vertice totali: 2 | Precedenze attivate: 59 (in 52/300 ep.) | Action-Masking: 3017 | Anti-Livelock: 1916
- Droni non arrivati (3 totali, media 1.00 per episodio fallito):
  - Rimasti bloccati nella stessa cella: 0/3 (0.0%)
  - In movimento continuo senza progredire: 3/3 (100.0%)

| Caso analizzato | Almeno una volta nell'episodio | Fino a fine episodio |
|:---|:---:|:---:|
| Contesa casella ai lati dell'hangar | 0/3 (0.0%) | 0/3 (0.0%) |
| Spazio di 1 cella tra montagna e bordo | 0/3 (0.0%) | 0/3 (0.0%) |

#### Confronto diretto MAPPO (Standard vs Precedenza + Masking + Anti-Livelock)

| Metrica | Senza Precedenza (Standard) | Con Precedenza + Masking + Anti-Livelock | Differenza |
|:---|:---:|:---:|:---:|
| Episodi completati | 64/300 (21.3%) | 297/300 (99.0%) | +233 |
| Scontri di vertice | 7444 | 2 | -7442 |
| Interventi regola di precedenza | 0 | 59 (in 52 ep.) | +59 |
| Interventi Action Masking | 0 | 3017 | +3017 |
| Interventi Anti-Livelock | 0 | 1916 | +1916 |
| Contesa lati hangar (persistente) | 22 | 0 | -22 |
| Varco 1 cella sul bordo (persistente) | 29 | 0 | -29 |

### Risultati PPO - SENZA PRECEDENZA (standard) (300 episodi sui semi `[42, 123, 999]`)
- Episodi completati: 141/300 (47.0%)
- Episodi falliti: 159/300 (53.0%)
- Scontri di vertice totali: 6002 | Precedenze attivate: 0 (in 0/300 ep.) | Action-Masking: 0 | Anti-Livelock: 0
- Droni non arrivati (305 totali, media 1.92 per episodio fallito):
  - Rimasti bloccati nella stessa cella: 265/305 (86.9%)
  - In movimento continuo senza progredire: 40/305 (13.1%)

| Caso analizzato | Almeno una volta nell'episodio | Fino a fine episodio |
|:---|:---:|:---:|
| Contesa casella ai lati dell'hangar | 16/159 (10.1%) | 15/159 (9.4%) |
| Spazio di 1 cella tra montagna e bordo | 38/159 (23.9%) | 37/159 (23.3%) |

### Risultati PPO - CON PRECEDENZA + ACTION MASKING + ANTI-LIVELOCK (300 episodi sui semi `[42, 123, 999]`)
- Episodi completati: 300/300 (100.0%)
- Episodi falliti: 0/300 (0.0%)
- Scontri di vertice totali: 3 | Precedenze attivate: 52 (in 49/300 ep.) | Action-Masking: 319 | Anti-Livelock: 132
- Nessun episodio fallito (100% di successo).

#### Confronto diretto PPO (Standard vs Precedenza + Masking + Anti-Livelock)

| Metrica | Senza Precedenza (Standard) | Con Precedenza + Masking + Anti-Livelock | Differenza |
|:---|:---:|:---:|:---:|
| Episodi completati | 141/300 (47.0%) | 300/300 (100.0%) | +159 |
| Scontri di vertice | 6002 | 3 | -5999 |
| Interventi regola di precedenza | 0 | 52 (in 49 ep.) | +52 |
| Interventi Action Masking | 0 | 319 | +319 |
| Interventi Anti-Livelock | 0 | 132 | +132 |
| Contesa lati hangar (persistente) | 15 | 0 | -15 |
| Varco 1 cella sul bordo (persistente) | 37 | 0 | -37 |

### Risultati su 300 episodi per algoritmo (semi `42, 123, 999`)

| Metrica | MAPPO (Standard) | MAPPO (Precedenza + Mask + Anti-Loop) | $\Delta$ MAPPO | PPO (Standard) | PPO (Precedenza + Mask + Anti-Loop) | $\Delta$ PPO |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Episodi completati** | 64 / 300 (21.3%) | **297 / 300 (99.0%)** | **+233 (+77.7%)** | 141 / 300 (47.0%) | **300 / 300 (100.0%)** | **+159 (+53.0%)** |
| **Scontri di vertice totali** | 7.444 | **2** | **-7.442 (-100.0%)** | 6.002 | **3** | **-5.999 (-100.0%)** |
| **Interventi regola precedenza** | 0 | **59** (in 52 ep.) | +59 | 0 | **52** (in 49 ep.) | +52 |
| **Interventi Action Masking** | 0 | **3.017** | +3.017 | 0 | **319** | +319 |
| **Interventi Anti-Livelock** | 0 | **1.916** | +1.916 | 0 | **132** | +132 |
| **Contesa lati hangar (persistente)** | 22 / 236 (9.3%) | **0 / 3 (0.0%)** | **-22 (-100.0%)** | 15 / 159 (9.4%) | **0 / 0 (0.0%)** | **-15 (-100.0%)** |
| **Varco 1 cella sul bordo (persistente)** | 29 / 236 (12.3%) | **0 / 3 (0.0%)** | **-29 (-100.0%)** | 37 / 159 (23.3%) | **0 / 0 (0.0%)** | **-37 (-100.0%)** |
