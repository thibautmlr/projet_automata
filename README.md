\# `automata\_extensions` — Extension pédagogique de `automata-lib` (9.2.0)



`automata\_extensions` enrichit la bibliothèque Python \*\*`automata-lib==9.2.0`\*\* sans jamais modifier son code source d'origine\[cite: 2]. Conçue selon une architecture par \*\*héritage multiple et mixins\*\*, elle couvre l'ensemble des algorithmes classiques de théorie des langages et des automates finis : analyse de graphes, déterminisation, minimisation (Myhill–Nerode et Brzozowski), conversions vers expressions régulières (élimination d'états, heuristique gloutonne, lemme d'Arden), construction de Thompson, quotients, résiduels, morphismes, monoïde syntaxique, grammaires régulières, visualisation (DOT, TikZ, LaTeX, SVG, PNG, PDF) et simulation interactive HTML\[cite: 1, 2].



\---



\## 1. Installation et tests



\### Installation locale en mode éditable

Depuis la racine du dépôt :



```bash

pip install -e .

```



\*(Optionnel : pour le rendu SVG/PNG/PDF, le binaire système Graphviz `dot` doit être installé et présent dans le `PATH`.)\*\[cite: 1, 2]



\### Exécution de la suite de tests (`pytest`)



```bash

python -m pytest

```



\---



\## 2. Architecture logicielle



\### Hiérarchie de classes (`ExtendedFA`, `ExtendedDFA`, `ExtendedNFA`, `ExtendedGNFA`)



Les algorithmes indépendants du déterminisme (95 % de la base de code) sont factorisés dans \*\*`ExtendedFA`\*\*, tandis que les algorithmes spécifiques sont isolés dans des mixins dédiés à `ExtendedDFA` ou `ExtendedNFA`\[cite: 2] :



```text

&#x20;                   automata.fa.fa.FA

&#x20;                           │

&#x20;                      ExtendedFA

&#x20;  ┌────────────────────────┼────────────────────────┐

&#x20;  │ (Graphes \& Analyse)    │ (Conversions \& Regex)  │ (Rendu \& Simulation)

&#x20;  ├─ GraphMixin            ├─ LanguageOperations    ├─ VisualizationMixin

&#x20;  ├─ AccessibilityMixin    ├─ ReverseMixin          ├─ AnimationMixin

&#x20;  ├─ TraversalMixin        ├─ RegexMixin            └─ GrammarMixin

&#x20;  ├─ CycleMixin            ├─ RegexOptimumMixin

&#x20;  ├─ SCCMixin              ├─ ArdenMixin

&#x20;  ├─ SubautomatonMixin     ├─ BrzozowskiMixin

&#x20;  ├─ DeterminismMixin      ├─ QuotientMixin

&#x20;  └─ WordMixin             └─ MorphismMixin

&#x20;         │                                 │

&#x20;         ▼                                 ▼

&#x20;    ExtendedDFA                       ExtendedNFA

&#x20;  (hérite aussi de DFA)             (hérite aussi de NFA)

&#x20;  ├─ CompletenessMixin              ├─ EpsilonMixin

&#x20;  ├─ ComplementMixin                ├─ EliminationMixin

&#x20;  ├─ ProductMixin                   ├─ DeterminizationMixin

&#x20;  ├─ UnionMixin                     ├─ ThompsonMixin

&#x20;  ├─ DifferenceMixin                └─ ExecutionMixin

&#x20;  ├─ InclusionMixin

&#x20;  ├─ IsomorphismMixin

&#x20;  ├─ PrefixMixin

&#x20;  ├─ MinimizationMixin

&#x20;  ├─ MinimizationExtraMixin

&#x20;  ├─ ResidualMixin

&#x20;  └─ SyntacticMonoidMixin

```



\### Principes de conception

\* \*\*Immutabilité stricte\*\* : aucune méthode ne modifie `self` ; toute transformation (`trim()`, `complete()`, `minimize()`, `to\_dfa()`, etc.) renvoie une nouvelle instance\[cite: 2].

\* \*\*Compatibilité `automata-lib==9.2.0`\*\* :

&#x20; \* `patch\_cached\_method()` corrige à l'import le descripteur `@cached\_method` afin d'autoriser les appels chaînés sur des instances temporaires (ex. `(d - d).is\_empty()`)\[cite: 1].

&#x20; \* `input\_parameters` collecte les attributs sur l'ensemble du MRO afin de préserver `copy()`, `copy.deepcopy()` et la sérialisation\[cite: 1].



\### Organisation des fichiers



```text

automata\_extensions/

├── \_\_init\_\_.py

├── utils/

│   └── patches.py                 # Correctif @cached\_method

├── grammar/

│   ├── \_\_init\_\_.py

│   └── grammar.py                 # Grammar (linéaire droite) \& DerivationStep

└── fa/

&#x20;   ├── \_\_init\_\_.py

&#x20;   ├── fa.py                      # Classe commune ExtendedFA

&#x20;   ├── dfa.py                     # Classe ExtendedDFA

&#x20;   ├── nfa.py                     # Classe ExtendedNFA

&#x20;   ├── gnfa.py                    # Classe ExtendedGNFA

&#x20;   ├── fa\_mixins/                 # Mixins communs à tous les automates finis

&#x20;   ├── dfa\_mixins/                # Mixins spécifiques aux DFA

&#x20;   └── nfa\_mixins/                # Mixins spécifiques aux NFA

tests/

├── conftest.py

└── test\_step1\_\*.py ... test\_step10\_\*.py

```



\---



\## 3. Exemples d'utilisation



\### Analyse structurelle, complétion et minimisation (Myhill–Nerode)



```python

from automata\_extensions.fa import ExtendedDFA



\# Automate reconnaissant les mots sur {a, b} ayant un nombre de 'a' multiple de 3

d = ExtendedDFA(

&#x20;   states={"0", "1", "2"},

&#x20;   input\_symbols={"a", "b"},

&#x20;   transitions={

&#x20;       "0": {"a": "1", "b": "0"},

&#x20;       "1": {"a": "2", "b": "1"},

&#x20;       "2": {"a": "0", "b": "2"},

&#x20;   },

&#x20;   initial\_state="0",

&#x20;   final\_states={"0"},

)



print(d.accepts("aababa"))          # True

print(d.run("aab"))                 # 0 --a--> 1 --a--> 2 --b--> 2 (reject)

print(d.is\_trim())                  # True

print(d.is\_minimal())               # True

print(d.equivalence\_classes())      # \[frozenset({'0'}), frozenset({'1'}), frozenset({'2'})]

d.print\_pair\_table(show\_round=True) # Table triangulaire de marquage des paires

```



\### Construction de Thompson, déterminisation et expressions régulières



```python

from automata\_extensions.fa import ExtendedNFA



nfa = ExtendedNFA.from\_regex("(a|b)\*abb", input\_symbols={"a", "b"})

dfa\_min = nfa.to\_dfa().minify()



print(dfa\_min.accepts("aabb"))      # True

print(dfa\_min.to\_regex\_optimum())   # Expression régulière compacte équivalente

print(dfa\_min.to\_regex\_arden())     # Résolution par le lemme d'Arden

```



\### Quotients, résiduels, monoïde syntaxique et grammaires régulières



```python

\# Quotients gauche/droit par un mot et automate des résiduels

lq = d.left\_quotient\_word("a")       # u^{-1}L

rq = d.right\_quotient\_word("a")      # L.u^{-1}

res = d.residual\_automaton()         # Automate déterministe minimal des résiduels



\# Monoïde syntaxique (transformations engendrées par l'alphabet)

print(len(d.syntactic\_monoid()))     # 3



\# Conversion bidirectionnelle automate <-> grammaire régulière

gram = d.to\_grammar()

print(gram.derive("aaa"))            # Liste des DerivationStep

```



\### Visualisation et animation HTML interactive



```python

print(d.to\_dot())                    # Source Graphviz DOT

print(d.to\_tikz())                   # Figure LaTeX TikZ

d.to\_svg("automate.svg")             # Export SVG via Graphviz

d.animate("aab", filename="sim.html")# Lecteur pas-à-pas HTML/SVG autonome

```



\---



\## 4. Schémas d'automates



\### Exemple : automate modulo 3 (`d`)



```text

&#x20;         b               b               b

&#x20;        ┌─┐             ┌─┐             ┌─┐

&#x20;        ▼ │             ▼ │             ▼ │

──► (( 0 )) ──── a ───► ( 1 ) ──── a ───► ( 2 )

&#x20;      ▲                                    │

&#x20;      └────────────────── a ───────────────┘

```



\### Code Graphviz DOT généré par `d.to\_dot()`



```dot

digraph Automaton {

&#x20;   rankdir="LR";

&#x20;   node \[fontname="Helvetica", fontsize=11];

&#x20;   edge \[fontname="Helvetica", fontsize=10];

&#x20;   \_\_start\_\_ \[shape=point, width=0.15];

&#x20;   s0 \[label="0", shape=doublecircle];

&#x20;   s1 \[label="1", shape=circle];

&#x20;   s2 \[label="2", shape=circle];

&#x20;   \_\_start\_\_ -> s0;

&#x20;   s0 -> s0 \[label="b"];

&#x20;   s0 -> s1 \[label="a"];

&#x20;   s1 -> s1 \[label="b"];

&#x20;   s1 -> s2 \[label="a"];

&#x20;   s2 -> s0 \[label="a"];

&#x20;   s2 -> s2 \[label="b"];

}

```



\### Code LaTeX TikZ généré par `d.to\_tikz()`



```latex

\\begin{tikzpicture}\[->, >=Stealth, shorten >=1pt, auto, thick]

&#x20;   \\node\[state, initial, accepting] (q0) at (-2.8, 0.0) {0};

&#x20;   \\node\[state] (q1) at (1.4, 2.42) {1};

&#x20;   \\node\[state] (q2) at (1.4, -2.42) {2};

&#x20;   \\path

&#x20;       (q0) edge\[loop above] node {b} (q0)

&#x20;       (q0) edge node {a} (q1)

&#x20;       (q1) edge\[loop above] node {b} (q1)

&#x20;       (q1) edge node {a} (q2)

&#x20;       (q2) edge node {a} (q0)

&#x20;       (q2) edge\[loop above] node {b} (q2);

\\end{tikzpicture}

```



\---



\## 5. Explication des principaux algorithmes



1\. \*\*Accessibilité, coaccessibilité et émondage (`trim`)\*\* :

&#x20;  \* Les états accessibles sont calculés par parcours BFS/DFS depuis l'état initial.

&#x20;  \* Les états coaccessibles sont obtenus par parcours sur l'automate renversé (`reverse()`) depuis les états finaux.

&#x20;  \* `trim()` restreint l'automate à l'intersection (états utiles)\[cite: 2].

2\. \*\*Composantes fortement connexes (`strongly\_connected\_components`)\*\* :

&#x20;  \* Implémentation de l'\*\*algorithme de Tarjan\*\* en un seul parcours en profondeur avec pile d'exploration et calcul des indices `lowlink`\[cite: 1, 2].

3\. \*\*Déterminisation (`to\_dfa`) et suppression des $\\varepsilon$-transitions\*\* :

&#x20;  \* Calcul des fermetures $\\varepsilon$ par BFS (`epsilon\_closure`), puis construction des sous-ensembles accessibles (algorithme de Rabin–Scott)\[cite: 2].

4\. \*\*Minimisation de Myhill–Nerode (`minimize`, `minify`, `pair\_table\_str`)\*\* :

&#x20;  \* Complétion préalable de l'automate avec un état puits `'⊥'`.

&#x20;  \* Séparation initiale des paires $(p, q)$ selon $(p \\in F) \\neq (q \\in F)$ (passe 0), puis raffinement itératif jusqu'au point fixe dès qu'un symbole $a \\in \\Sigma$ envoie $(p, q)$ vers une paire déjà distinguée\[cite: 1, 2].

5\. \*\*Minimisation de Brzozowski (`brzozowski\_minimize`)\*\* :

&#x20;  \* Applique la propriété théorique $\\min(A) \\cong \\text{det}(\\text{rev}(\\text{det}(\\text{rev}(A))))$ sans recourir au calcul explicite des classes d'équivalence.

6\. \*\*Conversions vers expressions régulières (`to\_regex`, `to\_regex\_optimum`, `to\_regex\_arden`)\*\* :

&#x20;  \* \*\*Élimination d'états (GNFA)\*\* : ajout d'une source unique et d'un puits unique reliés par $\\varepsilon$, puis élimination successive des états intermédiaires via $R\_{p,r} \\leftarrow R\_{p,r} \\mid R\_{p,q} R\_{q,q}^\* R\_{q,r}$\[cite: 1].

&#x20;  \* \*\*Heuristique optimale\*\* : sélectionne à chaque pas l'état minimisant le produit des degrés entrant/sortant et la taille des expressions (exploration exhaustive des permutations pour $|Q| \\le 5$).

&#x20;  \* \*\*Lemme d'Arden\*\* : résout le système d'équations linéaires droites $X\_i = \\bigcup\_j A\_{i,j} X\_j \\cup B\_i$ par élimination de Gauss utilisant $X = AX \\cup B \\implies X = A^\*B$\[cite: 1].

7\. \*\*Construction de Thompson (`from\_regex`)\*\* :

&#x20;  \* Tokenisation, insertion de la concaténation implicite, conversion postfixée (Shunting-Yard) et assemblage inductif de fragments à entrée unique et sortie unique reliés par des transitions $\\varepsilon$.



\---



\## 6. Complexités temporelles



Notations : $|Q|$ nombre d'états, $|\\Sigma|$ taille de l'alphabet, $|E| \\le |Q|^2 |\\Sigma|$ nombre de transitions, $|w|$ longueur du mot en entrée\[cite: 2].



| Catégorie | Méthode(s) | Complexité temporelle | Remarques |

| :--- | :--- | :--- | :--- |

| \*\*Parcours \& Graphes\*\* | `bfs`, `dfs`, `accessible\_states`, `coaccessible\_states`, `trim` | $\\mathcal{O}(\\|Q\\| + \\|E\\|)$ | Parcours linéaire du graphe |

| \*\*Structure\*\* | `strongly\_connected\_components`, `has\_cycle`, `is\_empty`, `is\_finite` | $\\mathcal{O}(\\|Q\\| + \\|E\\|)$ | Algorithme de Tarjan / DFS |

| \*\*Simulation\*\* | `accepts`, `run`, `execution\_trace` (DFA) | $\\mathcal{O}(\\|w\\|)$ | Transition unique par symbole |

| \*\*Simulation\*\* | `accepts`, `run`, `execution\_trace` (NFA) | $\\mathcal{O}(\\|w\\| \\cdot \\|Q\\|^2)$ | Propagation des $\\varepsilon$-fermetures |

| \*\*Complétion \& Complément\*\* | `complete`, `complement`, `is\_universal` | $\\mathcal{O}(\\|Q\\| \\cdot \\|\\Sigma\\|)$ | Ajout éventuel de l'état puits `'⊥'` |

| \*\*Produit \& Relations\*\* | `product`, `intersection`, `union`, `difference`, `is\_included\_in`, `is\_equivalent`, `counterexample` | $\\mathcal{O}(\\|Q\_1\\| \\cdot \\|Q\_2\\| \\cdot \\|\\Sigma\\|)$ | Produit synchronisé accessible |

| \*\*Isomorphisme\*\* | `is\_isomorphic\_to` | $\\mathcal{O}(\\|Q\\| \\cdot \\|\\Sigma\\|)$ | Bijection déterministe depuis l'état initial |

| \*\*Minimisation\*\* | `minimize`, `minify`, `equivalence\_classes`, `is\_minimal` | $\\mathcal{O}(\\|\\Sigma\\| \\cdot \\|Q\\|^2)$ | Raffinement des paires de Myhill–Nerode |

| \*\*$\\varepsilon$-transitions\*\* | `epsilon\_closure`, `remove\_epsilon\_transitions` | $\\mathcal{O}(\\|Q\\|^3 + \\|Q\\|^2 \\|\\Sigma\\|)$ | Clôture transitive des arcs $\\varepsilon$ |

| \*\*Déterminisation\*\* | `determinize`, `to\_dfa` | $\\mathcal{O}(2^{\\|Q\\|} \\cdot \\|\\Sigma\\|)$ | Pire cas exponentiel (construction des sous-ensembles) |

| \*\*Brzozowski\*\* | `brzozowski\_minimize` | $\\mathcal{O}(2^{2^{\\|Q\\|}})$ | Double déterminisation sur automate renversé |

| \*\*Thompson\*\* | `ExtendedNFA.from\_regex` | $\\mathcal{O}(\\|r\\|)$ | Linéaire en la longueur $\\|r\\|$ de la regex |

| \*\*Automate $\\to$ Regex\*\* | `to\_regex`, `to\_regex\_optimum`, `to\_regex\_arden` | $\\mathcal{O}(\\|Q\\|^3)$ opérations regex | Taille de sortie pouvant croître exponentiellement |

| \*\*Quotients \& Résiduels\*\* | `left\_quotient\_word`, `right\_quotient\_word` | $\\mathcal{O}(\\|w\\| \\cdot \\|Q\\|^2 + \\|E\\|)$ | Lecture de $w$ puis construction du quotient |

| \*\*Monoïde syntaxique\*\* | `syntactic\_monoid` | $\\mathcal{O}(\\|M\\| \\cdot \\|\\Sigma\\| \\cdot \\|Q\_{\\min}\\|)$ | $\\|M\\| \\le \\|Q\_{\\min}\\|^{\\|Q\_{\\min}\\|}$ |

| \*\*Grammaires\*\* | `to\_grammar`, `Grammar.to\_nfa` | $\\mathcal{O}(\\|Q\\| + \\|E\\|)$ | Correspondance linéaire droite $\\leftrightarrow$ NFA |

| \*\*Visualisation\*\* | `to\_dot`, `to\_tikz`, `to\_latex`, `animate` | $\\mathcal{O}(\\|Q\\| + \\|E\\|)$ | Génération textuelle / HTML autonome |

