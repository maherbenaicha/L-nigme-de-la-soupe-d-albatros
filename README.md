# Mystery Agents — poser les bonnes questions

Prototype Python 3.10+, sans dépendance externe. Trois stratégies utilisent le même modèle : historique seul (`naive`), mémoire explicite (`structured`), sélection de questions par gain d'information calculé (`information_gain`). Aucune recherche web. La baseline dispose du même historique ; elle n'est pas artificiellement amnésique.

Sur cette machine, `python` n'est pas dans le PATH. `./run.ps1 --demo` utilise automatiquement le Python fourni avec Codex lorsqu'il est présent. Les mêmes arguments sont acceptés : `./run.ps1 --model identifiant-du-modele --trials 3`.

## Démarrage (PowerShell)

### Groq avec `.env`

Le fichier `.env` à la racine est chargé automatiquement, sans dépendance. Utiliser les noms suivants (voir `.env.example`) :

```dotenv
AI_PROVIDER=groq
GROQ_API_KEY=votre-cle-groq
GROQ_MODEL=llama-3.3-70b-versatile
```

Lancer `./run.ps1 --trials 1 --max-questions 4`. Une clé `GROQ_API_KEY` sélectionne Groq automatiquement sauf choix explicite via `--provider` ou `AI_PROVIDER`. Les variables du terminal priment sur `.env`. `--model` prime sur le modèle configuré. Le fichier `.env` est ignoré par Git et son contenu n'est jamais exporté. L'interface suit la [documentation Groq](https://console.groq.com/docs/api-reference).

### OpenAI

```powershell
python -m unittest -v
python experiment.py --demo
$env:OPENAI_API_KEY = "votre-cle"
$env:OPENAI_MODEL = "identifiant-du-modele"
python experiment.py --provider openai --trials 3 --max-questions 15
```

Choisir un modèle compatible Chat Completions et le mode JSON. La clé reste dans l'environnement, jamais dans les exports. Interface vérifiée avec la [documentation officielle OpenAI](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create).

`--demo` vérifie uniquement les exports avec des valeurs synthétiques identiques pour les trois stratégies. Il ne simule pas une victoire d'une stratégie et ne produit aucun résultat scientifique.

## Protocole

- Chaque épisode repart sans mémoire des autres épisodes. Ordre mélangé avec `--seed` (cela ne rend pas le modèle déterministe).
- L'agent ne reçoit que l'énoncé et ses réponses précédentes. Seul l'arbitre reçoit la solution et la grille de correction. Aucun outil externe n'est exposé aux agents.
- L'arbitre répond `yes`, `no`, `irrelevant`. Une question ambiguë, multiple ou non déterminée par les faits est classée `irrelevant` et consomme une question.
- Une seule proposition de solution est autorisée. L'agent peut répondre dès le début ; une réponse finale est demandée après épuisement du budget.
- L'agent structuré conserve des faits et hypothèses. Le troisième génère 3 à 8 hypothèses pondérées et questions candidates. Python calcule H(hypothèses) − somme P(réponse) × H(hypothèses | réponse), puis choisit le maximum. Les probabilités et réponses hypothétiques restent des estimations du modèle : ce n'est pas un gain réel garanti.
- Même budget de questions et même limite de tokens par appel. La taille des sorties et le nombre de tokens effectivement consommés peuvent varier : c'est une mesure de l'expérience, pas un budget total de calcul égalisé.

## Résultats et audit

Chaque exécution crée un répertoire daté dans `results/` : configuration, copie figée du jeu d'énigmes, traces JSON par épisode, appels et usage API par rôle, puis `episodes.csv`. Le terminal affiche un compteur de questions et les réponses, utilisable pour une capture vidéo.

Les tokens de l'agent incluent ses hypothèses, candidats et mémoire. Ceux de l'arbitre et du correcteur sont séparés. Les tokens inconnus restent vides, jamais remplacés par une estimation. Ajouter `--input-price 0.00 --output-price 0.00` avec les tarifs réels par million de tokens pour obtenir un coût total estimé en USD. Ce calcul simple utilise le tarif d'entrée non mis en cache et peut surestimer la facture en cas de cache ; aucun tarif n'est embarqué.

Le taux de réussite affiché inclut les erreurs dans le dénominateur ; leur nombre est affiché séparément. La moyenne des questions est conditionnée aux réussites : toujours la lire avec le taux de réussite et les échecs. Une réponse immédiate correcte vaut zéro question. Les traces permettent un classement ultérieur, sans prétendre qu'un agent gagnant sur trois énigmes est supérieur en général.

## Avant une publication

Les trois énigmes proposées ici sont des exemples rédigés pour le prototype, sans garantie d'inédit ou de difficulté comparable. Elles demandent une relecture humaine et une vérification de leur cohérence. Ne pas utiliser l'énigme célèbre de l'albatros comme preuve principale : la mémorisation peut remplacer la déduction.

Préparer un jeu privé plus large, figer les grilles et les prompts avant les essais, effectuer plusieurs répétitions et auditer les décisions de l'arbitre. Un arbitre LLM peut être incohérent et favoriser des formulations produites par le même modèle. Les exemples inventés peuvent avoir des solutions alternatives : les examiner avant de tirer une conclusion. Ne pas présenter les résultats de démonstration comme des mesures réelles.

Pour ajouter des énigmes : fournir un tableau JSON d'objets `id`, `statement`, `solution`, `rubric` (liste des éléments causaux indispensables), puis lancer avec `--puzzles chemin.json`.

Titre possible après de vraies mesures : « Can an AI solve a mystery in fewer questions? I challenged 3 AI agents. »
