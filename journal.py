#!/usr/bin/env python3
"""
writerdeck journal — a daily writing practice tool.
Entries are write-once and saved as plain text.

Usage:
    python3 journal.py
"""

import curses
import os
import random
import sys
import textwrap
import time
import locale
locale.setlocale(locale.LC_ALL, '')
from datetime import datetime, timedelta

# ── Config ──────────────────────────────────────────────────────────────────

JOURNAL_DIR = os.path.expanduser("~/journal")
FILE_EXT = ".txt"
TAB_WIDTH = 4

# ── Suggestions d'écriture ───────────────────────────────────────────────────

PROMPTS = [
    "Que s'est-il passé aujourd'hui ?",
    "Quelle a été la meilleure chose qui s'est passée aujourd'hui ?",
    "Quelle a été la pire chose qui s'est passée aujourd'hui ?",
    "Quelle est la chose la plus intéressante que j'ai vue ou entendue aujourd'hui ?",
    "Quel a été le défi le plus difficile que j'ai affronté aujourd'hui ?",
    "Pour quoi suis-je reconnaissant(e) aujourd'hui ?",
    "Qu'ai-je appris aujourd'hui ?",
    "Quelle a été la chose la plus amusante que j'ai faite aujourd'hui ?",
    "Quelle a été la chose la plus surprenante qui s'est passée aujourd'hui ?",
    "Qu'ai-je fait aujourd'hui dont je suis fier/fière ?",
    "Quels sont mes objectifs et buts liés à ce problème ou défi ?",
    "Quelles sont les solutions possibles à ce problème ou défi ?",
    "Quelles solutions créatives et non conventionnelles puis-je envisager ?",
    "Quels sont les avantages et inconvénients de chaque solution potentielle ?",
    "Comment puis-je collaborer avec d'autres pour trouver une solution ?",
    "Quelles ressources puis-je utiliser pour aider à résoudre ce problème ou défi ?",
    "Comment puis-je appliquer mes compétences, mes connaissances et mon expérience à ce problème ou défi ?",
    "Quels sont les obstacles potentiels à la mise en œuvre d'une solution, et comment puis-je les surmonter ?",
    "Comment puis-je prioriser et organiser mes pensées et idées pour résoudre efficacement ce problème ou défi ?",
    "Quelles croyances ou messages sur mon corps dois-je laisser aller pour cultiver plus d'amour-propre et d'acceptation ?",
    "Quelles activités ou pratiques m'aident à me sentir connecté(e) à mon corps et en harmonie avec lui ?",
    "Comment puis-je être plus compatissant(e) envers mon corps, surtout quand je me sens autocritique ou négatif(ve) ?",
    "Quel rôle jouent les réseaux sociaux ou les médias en général dans la construction de mon image corporelle, et comment puis-je cultiver une relation plus positive avec ces sources d'influence ?",
    "Comment me sentirais-je si je laissais tomber le besoin de comparer mon corps à celui des autres, et si je me concentrais plutôt sur mes propres forces et ma beauté unique ?",
    "Quelles sont les façons dont je peux prioriser ma santé physique et mon bien-être, sans tomber dans le piège de la culture des régimes ou de la honte corporelle ?",
    "Comment puis-je passer d'objectifs basés sur l'apparence (ex : perte de poids, atteindre une certaine forme corporelle) à des mesures plus holistiques de la santé et du bien-être (ex : niveaux d'énergie, humeur, force, etc.) ?",
    "Que signifie vraiment incarner l'amour de soi et la positivité corporelle, et comment puis-je faire de petits pas vers cela chaque jour ?",
    "Comment puis-je cultiver un sentiment d'appréciation et d'amour pour mon corps, même s'il ne correspond pas aux idéaux sociétaux ?",
    "Quelles sont les façons dont je peux célébrer et prendre soin de mon corps, quelle que soit sa forme ou sa taille ?",
    "Comment est-ce que j'utilise ma créativité au quotidien ?",
    "Quelle est une chose que j'ai toujours voulu créer, et quelles étapes puis-je prendre pour la réaliser ?",
    "Quel est un endroit ou un environnement qui inspire ma créativité, et comment puis-je créer plus d'opportunités pour y être ?",
    "Quelles sont mes passions et mes intérêts, et comment puis-je les intégrer dans ma vie professionnelle ou personnelle ?",
    "Quel est un petit projet créatif que je peux faire aujourd'hui, et comment puis-je le rendre unique à mon style personnel ?",
    "Quelle est une peur ou un obstacle qui me bloque créativement, et que puis-je faire pour le surmonter ?",
    "Qu'est-ce que je peux apprendre ou expérimenter pour développer mes compétences et connaissances créatives ?",
    "Quel est un défi ou une contrainte que je peux me donner pour me pousser créativement ?",
    "Quelle est une façon dont je peux exprimer de la gratitude, de l'amour ou de l'appréciation de manière créative pour quelqu'un dans ma vie ?",
    "Comment puis-je me défier de sortir des sentiers battus et d'embrasser des idées nouvelles et créatives ?",
    "Comment puis-je m'entourer de personnes et d'environnements qui favorisent la créativité et l'inspiration ?",
    "Quelles sont les façons dont je peux prendre du temps pour moi et recharger mes batteries pour cultiver la créativité et l'inspiration ?",
    "Quels sont les loisirs ou activités que je peux poursuivre pour puiser dans ma créativité et mon imagination ?",
    "Comment puis-je intégrer plus de jeu et de plaisir dans ma vie pour favoriser la créativité et l'inspiration ?",
    "Quelles sont les façons dont je peux sortir de ma zone de confort et essayer de nouvelles choses pour stimuler la créativité et l'inspiration ?",
    "Comment puis-je être plus ouvert(e) d'esprit et réceptif(ve) aux nouvelles idées et perspectives ?",
    "Quelles sont les façons dont je peux utiliser la technologie et l'innovation pour améliorer ma créativité et mon inspiration ?",
    "Comment puis-je chercher de nouvelles expériences et aventures pour élargir mes horizons et inspirer ma créativité ?",
    "Comment puis-je créer un environnement bienveillant et nourrissant pour mon esprit, mon corps et mon âme afin d'encourager la créativité et l'inspiration ?",
    "Écris une histoire du point de vue d'un objet inanimé qui prend vie.",
    "Écris un poème sur un souvenir d'enfance qui t'est resté.",
    "Écris sur un personnage qui se réveille un jour avec un super-pouvoir.",
    "Écris un poème sur le changement des saisons et la beauté de la nature.",
    "Écris une histoire qui commence par la phrase « La porte grinça en s'ouvrant, révélant une pièce depuis longtemps oubliée. »",
    "Écris une histoire sur un groupe de personnes coincées sur une île déserte.",
    "Écris un poème qui explore le concept du temps et la façon dont il façonne nos vies.",
    "Écris une histoire du point de vue d'un personnage qui a perdu la mémoire et essaie de reconstituer son passé.",
    "Écris un poème qui réfléchit à la beauté des moments quotidiens.",
    "Écris une histoire sur un voyageur temporel qui se retrouve accidentellement coincé à la mauvaise époque.",
    "Écris sur une relation qui t'a appris une leçon importante sur toi-même ou sur le monde qui t'entoure.",
    "Écris une histoire sur un personnage qui découvre un livre mystérieux avec un message caché.",
    "Écris un poème qui utilise le thème de l'eau pour transmettre un sens ou une émotion plus profond(e).",
    "Écris sur un endroit qui a eu un impact significatif sur ta vie, et les souvenirs ou émotions qu'il suscite en toi.",
    "Écris une histoire sur un personnage qui est contraint d'affronter sa peur la plus profonde.",
    "Écris un poème qui explore l'idée de chez-soi et ce que cela signifie pour toi.",
    "Écris une histoire du point de vue d'un animal qui essaie de survivre dans la nature sauvage.",
    "Écris sur une expérience qui t'a appris une précieuse leçon sur le pardon ou l'acceptation.",
    "Écris une histoire sur un personnage qui reçoit une lettre d'un parent perdu de vue contenant une révélation surprenante.",
    "Comment se sent mon corps aujourd'hui ?",
    "De quoi suis-je nerveux/nerveuse ou anxieux/anxieuse aujourd'hui ?",
    "Quelles actions puis-je prendre face à chacune des choses qui me rendent nerveux/nerveuse ou anxieux/anxieuse ?",
    "Quelles sont mes priorités du jour ?",
    "Que puis-je faire pour rendre cette journée extraordinaire ?",
    "Qu'ai-je appris aujourd'hui ? Comment puis-je appliquer cette connaissance à l'avenir ?",
    "Quels défis ai-je affrontés aujourd'hui ? Comment les ai-je surmontés ? Qu'est-ce que ces expériences m'ont appris ?",
    "Qu'ai-je fait aujourd'hui qui m'a apporté de la joie ou de la satisfaction ? Comment puis-je intégrer davantage de ces activités dans ma routine quotidienne ?",
    "Quel a été un moment de joie, de plaisir ou de contentement aujourd'hui ?",
    "Quel petit détail ai-je remarqué aujourd'hui ?",
    "Quel temps faisait-il aujourd'hui ?",
    "Pour quoi suis-je reconnaissant(e) aujourd'hui ?",
    "Qu'aurais-je pu faire différemment aujourd'hui ?",
    "Comment puis-je rendre demain encore meilleur(e) ?",
    "Quelle est la décision que je dois prendre ?",
    "Quand dois-je prendre cette décision ?",
    "Quel est le résultat souhaité que j'espère atteindre ?",
    "Quels sont les avantages et inconvénients de chaque option ?",
    "Quelles sont mes peurs ou préoccupations concernant cette décision ?",
    "Quelles connaissances ou leçons ai-je tirées de décisions similaires prises dans le passé ?",
    "Comment ces leçons ou connaissances s'appliquent-elles à cette situation ?",
    "Quel conseil donnerais-je à un(e) ami(e) dans la même situation ?",
    "Qu'est-ce que mon instinct ou mon intuition me dit sur cette décision ?",
    "Quel impact cette décision aura-t-elle sur moi et sur les autres ?",
    "Comment cette décision s'aligne-t-elle avec mes valeurs ?",
    "De quelles ressources ou quel soutien ai-je besoin pour prendre cette décision avec confiance et clarté ?",
    "Quel est le pire scénario si je prends cette décision ?",
    "Quels faits ai-je pour soutenir ma décision ?",
    "Comment je me sens par rapport à ma décision ?",
    "À quel point me sens-je confiant(e) dans cette décision ?",
    "Quelles sont mes prochaines étapes pour cette décision ?",
    "Quel est le rêve le plus mémorable que j'ai fait la nuit dernière ? Note le plus de détails possible dont tu te souviens.",
    "Quels thèmes ou symboles récurrents apparaissent dans mes rêves ? Y a-t-il des schémas que je peux identifier ?",
    "Quelles émotions ai-je ressenties dans mon rêve, et sont-elles liées à des problèmes actuels dans ma vie éveillée ?",
    "Que pense-je que mon rêve essaie de me dire ? Comment puis-je appliquer son message à ma vie ?",
    "Si je pouvais avoir le rêve que je voulais cette nuit, de quoi serait-il question ?",
    "Si je pouvais poser n'importe quelle question à un personnage de rêve, qui choisirais-je et que lui demanderais-je ?",
    "Quels sont certains des rêves les plus bizarres ou surréalistes que j'ai jamais eus ? Que pense-je qu'ils signifient ?",
    "Quel est le type de rêve récurrents que j'ai (cauchemars, rêves où l'on vol, etc.) ? Qu'est ce que ça pourrait vouloir dire de moi ?",
    "Quelles sont trois choses qui se sont bien passées aujourd'hui, et pourquoi ?",
    "Quels ont été les moments forts de ma journée ?",
    "Quelles sont trois choses que j'aurais pu faire différemment aujourd'hui, et comment puis-je tirer des enseignements de ces expériences ?",
    "Qu'ai-je appris aujourd'hui ?",
    "Comment ai-je exprimé ma gratitude aujourd'hui ?",
    "Quels défis ai-je rencontrés aujourd'hui et comment les ai-je surmontés ?",
    "Qu'ai-je fait pour prendre soin de moi aujourd'hui ?",
    "Qu'ai-je fait pour aider les autres aujourd'hui ?",
    "Comment ai-je priorisé mon temps aujourd'hui ?",
    "Qu'ai-je fait pour apporter de la positivité dans ma journée ?",
    "Qu'ai-je fait aujourd'hui qui m'a rendu(e) fier/fière de moi-même ?",
    "Quels ont été les événements les plus importants de la journée ?",
    "Comment me suis-je senti(e) à différents moments tout au long de la journée ?",
    "Quels événements inattendus se sont produits aujourd'hui ?",
    "Avec qui ai-je interagi aujourd'hui et comment étaient ces interactions ?",
    "Qu'ai-je accompli aujourd'hui ?",
    "Quelles sont les choses que je voudrais faire différemment demain ?",
    "Qu'ai-je fait pour me détendre et me ressourcer aujourd'hui ?",
    "Quelles ont été certaines des vues, des sons et des odeurs que j'ai vécus aujourd'hui ?",
    "Comment ai-je géré les situations difficiles qui se sont présentées aujourd'hui ?",
    "Quelles sont certaines des choses auxquelles j'aspire pour demain ?",
    "Quelles émotions ai-je vécues aujourd'hui ?",
    "Comment ai-je répondu à chaque émotion ? Qu'est-ce qui a déclenché chaque émotion ?",
    "Qu'ai-je fait pour avoir un impact positif sur la journée de quelqu'un d'autre ?",
    "À quoi est-ce que j'aspire pour demain ?",
    "Que puis-je faire pour me préparer à une nuit de sommeil paisible ?",
    "Quel a été l'événement le plus significatif de ma journée et pourquoi était-il important ?",
    "Comment ai-je géré les conflits ou les situations difficiles aujourd'hui ?",
    "Qu'ai-je appris sur moi-même aujourd'hui ?",
    "Quelles sont les choses que je peux faire différemment demain pour avoir une journée encore meilleure ?",
    "Qui a eu un impact positif sur ma journée et comment ?",
    "Qu'ai-je fait pour améliorer la journée de quelqu'un d'autre ?",
    "Quelles sont les choses que je veux retenir de cette journée ?",
    "Quelle est la chose sotte qui me fait toujours rire ?",
    "Quel est un souvenir d'enfance préféré qui me procure encore de la joie ?",
    "Si je pouvais vivre à n'importe quelle époque ou endroit, où choisirais-je et pourquoi ?",
    "Quel est mon repas ou type de nourriture préféré, et pourquoi l'aimé-je tant ?",
    "Si je pouvais avoir n'importe quel super-pouvoir, lequel ce serait et pourquoi ?",
    "Quel est un livre ou film qui me met toujours de bonne humeur, et pourquoi ?",
    "Quelle est une chose que j'ai toujours voulu essayer mais que je n'ai pas encore faite ? Comment pourrais-je y parvenir ?",
    "Quelle est une chose dont je ne peux pas me passer ?",
    "Quelle est une anecdote amusante sur ma vie que je n'ai pas de mal à partager avec les autres ?",
    "Quelle est une chose sur moi-même que je sais être originale ?",
    "Si je pouvais être n'importe quel personnage fictif, qui choisirais-je et pourquoi ?",
    "Quelle est la tenue ou le déguisement le plus extravagant que j'ai jamais porté ? Où l'ai-je porté, et comment me suis-je senti(e) ?",
    "Quelle est ma blague ou mon jeu de mots préféré, et pourquoi me fait-il rire ?",
    "Quel est le meilleur cadeau que j'ai jamais offert, et pourquoi était-il si spécial ?",
    "Si j'étais un super-héros, quel serait mon nom, mes pouvoirs et mon costume ?",
    "Quelle est la farce la plus drôle que j'ai jamais faite à quelqu'un, ou qu'on m'a faite ?",
    "Si je pouvais magiquement échanger ma vie avec quelqu'un pour une journée, qui ce serait et pourquoi ?",
    "Quel est mon jouet ou jeu préféré de l'enfance, et pourquoi l'aimais-je tant ?",
    "Quel est mon mouvement de danse préféré, et puis-je l'enseigner à quelqu'un d'autre (ou le décrire en mots) ?",
    "Si je pouvais voyager n'importe où dans le monde (ou au-delà), où irais-je et que ferais-je là-bas ?",
    "Quels sont mes trois principaux objectifs pour l'année prochaine ?",
    "Quelles sont les étapes concrètes que je peux prendre pour atteindre mes objectifs ?",
    "Quelle est une nouvelle habitude que j'aimerais développer le mois prochain ?",
    "Comment puis-je créer un plan pour faire de cette nouvelle habitude une partie régulière de ma routine ?",
    "Quelles sont trois compétences ou domaines de connaissances que j'aimerais développer dans l'année à venir ?",
    "Quelles ressources ou quel soutien puis-je chercher pour m'aider à atteindre mes objectifs ?",
    "Quelles sont trois choses qui m'empêchent d'atteindre mes objectifs ?",
    "Comment puis-je travailler à surmonter ces obstacles ?",
    "Quels sont trois petits objectifs mesurables que je peux me fixer pour cette semaine ?",
    "Comment vais-je me tenir responsable de la réalisation de mes objectifs ?",
    "Quels sont mes objectifs professionnels à long terme ? Quelles étapes concrètes puis-je prendre pour m'en rapprocher ?",
    "Quelles sont mes valeurs personnelles et comment sont-elles liées à mes objectifs ?",
    "Comment puis-je m'assurer que mes objectifs sont alignés avec mes valeurs ?",
    "Quels sont les obstacles potentiels que je pourrais rencontrer en travaillant vers mes objectifs ?",
    "Comment puis-je élaborer un plan pour surmonter les obstacles à mes objectifs ?",
    "Comment puis-je suivre mes progrès vers mes objectifs ?",
    "Quels outils ou systèmes puis-je utiliser pour rester motivé(e) et sur la bonne voie ?",
    "Quels sont trois petits objectifs spécifiques que je peux me fixer chaque jour ?",
    "Comment puis-je m'assurer que mes actions quotidiennes s'alignent avec mes objectifs et priorités plus larges ?",
    "Quelles habitudes ai-je besoin pour atteindre mes objectifs ?",
    "Qui sont trois personnes dans ma vie pour lesquelles je suis reconnaissant(e), et pourquoi ?",
    "Quelles sont trois petites choses qui se sont passées aujourd'hui pour lesquelles je suis reconnaissant(e) ?",
    "Quelle est une chose que je tiens souvent pour acquise dans ma vie, et comment puis-je cultiver plus d'appréciation et de gratitude pour elle ?",
    "Quelles sont certaines qualités positives ou forces que je possède, et comment puis-je en être reconnaissant(e) ?",
    "Quelle est une chose dans ma vie dont je me sens « chanceux/chanceuse » d'avoir ?",
    "Quel est un plaisir simple que j'apprécie en ce moment ?",
    "Pour quoi suis-je reconnaissant(e) d'avoir appris récemment ?",
    "De quelle manière ai-je grandi en tant que personne au cours de l'année écoulée ?",
    "Qu'est-ce que j'aime dans l'endroit où je vis en ce moment ?",
    "Quels ont été certains moments de joie aujourd'hui ?",
    "Comment le fait d'exprimer ma gratitude me fait-il sentir en ce moment ?",
    "Comment puis-je exprimer ma gratitude aujourd'hui ?",
    "Quelles sont certaines façons dont je peux exprimer ma gratitude et apprécier la beauté et l'émerveillement du monde qui m'entoure ?",
    "Quels sont certains domaines de ma vie où j'ai tendance à avoir un état d'esprit fixe ?",
    "Comment puis-je changer ma façon de penser pour adopter plutôt un état d'esprit de croissance ?",
    "Quels sont certains objectifs que j'ai eu peur de poursuivre par peur de l'échec ou du rejet ?",
    "Comment puis-je recadrer mon état d'esprit pour voir l'échec comme une partie naturelle du processus d'apprentissage, et l'utiliser comme une opportunité de croissance ?",
    "Quelles sont certaines de mes croyances limitantes et de mes pensées intérieures qui pourraient me retenir ?",
    "Comment puis-je les remettre en question et les surmonter ?",
    "Comment puis-je embrasser les défis et les échecs comme des opportunités de croissance et de développement, plutôt que de les voir comme des revers ?",
    "Comment puis-je cultiver une attitude positive et optimiste, même face à l'adversité et aux difficultés ?",
    "Quelles sont certaines façons dont je peux chercher des retours et des critiques constructives pour continuer à grandir et à m'améliorer ?",
    "Comment puis-je viser le progrès plutôt que la perfection dans ma vie personnelle et professionnelle ?",
    "Quelles sont certaines de mes forces et de mes domaines de croissance, et comment puis-je utiliser cette connaissance pour conduire le développement et la croissance personnels ?",
    "Comment puis-je chercher de nouvelles expériences, opportunités et relations pour élargir mes horizons et soutenir la croissance personnelle ?",
    "Comment puis-je favoriser la résilience et la persévérance face aux obstacles et aux défis pour continuer à grandir et à me développer ?",
    "Comment puis-je assumer la responsabilité de mes pensées, de mes sentiments et de mes actions, et les utiliser comme des opportunités de croissance et de développement ?",
    "Comment puis-je voir les erreurs et les échecs comme des opportunités d'apprentissage, plutôt que comme des revers ou des obstacles ?",
    "Quelles sont certaines nouvelles compétences ou domaines de connaissances que je veux développer ?",
    "Comment puis-je cultiver une attitude curieuse et ouverte d'esprit, et chercher de nouvelles informations et connaissances pour soutenir la croissance et le développement ?",
    "Quelles sont certaines façons dont je peux adopter une approche proactive plutôt que réactive face aux défis et aux difficultés ?",
    "Quels souvenirs ai-je de mon enfance ? Y a-t-il des souvenirs heureux qui se démarquent ?",
    "Quelle était mon activité préférée quand j'étais enfant ? Avais-je des loisirs ou des intérêts que j'adorais ?",
    "Comment passais-je mon temps libre en tant qu'enfant ? À quels jeux jouais-je ? Quels livres lisais-je ?",
    "Qu'est-ce que j'aimais le plus à l'école ? Avais-je une matière ou un professeur préféré ?",
    "Avais-je des rêves ou des aspirations en tant qu'enfant ? Que voulais-je faire quand je serais grand(e) ?",
    "Quels étaient certains des défis ou des difficultés que j'ai rencontrés en tant qu'enfant ? Comment ces expériences m'ont-elles façonné(e) ?",
    "Comment ma famille et mon éducation ont-ils influencé mes expériences d'enfance ? Quelles influences positives ou négatives ai-je eues ?",
    "Quelles croyances ou attitudes ai-je développées en tant qu'enfant qui pourraient encore m'influencer aujourd'hui ?",
    "Comment puis-je nourrir et prendre soin de mon enfant intérieur maintenant ? Quelles activités ou expériences me procurent de la joie et de la légèreté ?",
    "Que puis-je apprendre de mon enfant intérieur ? Comment puis-je puiser dans la curiosité, la créativité et la résilience que j'avais en tant qu'enfant ?",
    "Quelles activités ou expériences me procuraient de la joie en tant qu'enfant ?",
    "Comment puis-je intégrer ces activités dans ma vie maintenant ?",
    "Comment puis-je nourrir mon enfant intérieur et cultiver un sens du jeu et de l'émerveillement ?",
    "Quand ai-je ressenti de l'inspiration pour la dernière fois ?",
    "Où trouvé-je habituellement de l'inspiration ?",
    "Quelles choses m'inspirent ?",
    "Qui est quelqu'un qui m'inspire, et quelles qualités possède-t-il/elle que j'admire ?",
    "Quel est un livre ou film qui m'a inspiré(e), et pourquoi ?",
    "Quelles sont certaines de mes formes d'art, de littérature ou de médias préférées, et comment peuvent-elles m'inspirer ?",
    "Quelle est une citation ou un dicton qui m'inspire, et comment puis-je appliquer sa sagesse à ma vie ?",
    "Quel est un projet créatif sur lequel j'ai voulu travailler, et quelles étapes puis-je prendre pour commencer ?",
    "Quand ai-je été complètement émerveillé(e) par quelque chose pour la dernière fois, et qu'est-ce qui a inspiré ce sentiment ?",
    "Quelle est une chose que j'ai toujours voulu apprendre, et comment puis-je trouver du temps pour poursuivre cet intérêt ?",
    "Quelle est une petite chose que je peux faire chaque jour pour cultiver un plus grand sens de l'inspiration et de la créativité dans ma vie ?",
    "Sur quoi veux-je me concentrer ce mois/cette semaine/aujourd'hui ?",
    "Quelles sont mes intentions pour la journée ?",
    "Quel est mon plus grand « pourquoi » (le but ou la motivation plus profond(e) derrière mes intentions) ?",
    "Comment puis-je utiliser mon « pourquoi » pour rester concentré(e) et engagé(e) ?",
    "Comment puis-je prioriser mon temps et mon énergie en conséquence ?",
    "Quels sont certains facteurs externes qui pourraient affecter ma capacité à me concentrer sur mes intentions, et comment puis-je planifier à l'avance pour y faire face ?",
    "Quelles sont certaines distractions ou pertes de temps que je dois éliminer afin de me concentrer sur ce qui est vraiment important ?",
    "Qu'est-ce qui me procure le plus de joie et de satisfaction, et comment puis-je faire du temps pour ces choses dans ma vie ?",
    "Que signifie le bonheur pour moi ? Que puis-je faire pour cultiver plus de bonheur et de contentement dans ma vie ?",
    "Quelles décisions dois-je prendre en ce moment ?",
    "Comment est-ce que je définis le succès ? Quelles étapes puis-je prendre pour y parvenir ?",
    "Quelles sont mes peurs et mes insécurités ? Comment puis-je les surmonter pour devenir plus confiant(e) et assuré(e) ?",
    "Quelles sont les relations les plus importantes dans ma vie ? Comment puis-je les renforcer ?",
    "En général, comment est-ce que je me sens par rapport à la façon dont ma vie évolue en ce moment ?",
    "Quels sont certains domaines de ma vie où je suis actuellement bloqué(e) ou stagnant(e) ? Quelles étapes puis-je prendre pour avancer et progresser dans ces domaines ?",
    "Quels thèmes, schémas ou symboles ai-je remarqués dans ma vie récemment ?",
    "Quelles sont certaines croyances ou suppositions que j'ai sur moi-même ou sur le monde qui m'entoure ?",
    "Lorsque je suis confronté(e) à des défis ou des obstacles, quelle est ma réaction habituelle ?",
    "Quelles sont certaines activités ou habitudes qui épuisent mon énergie ou ma motivation ?",
    "Comment est-ce que je gère habituellement mes émotions et mes sentiments ? Y a-t-il des émotions que j'ai tendance à éviter ou à réprimer ?",
    "Quelles sont certaines des choses pour lesquelles je suis le plus reconnaissant(e) dans ma vie ? Comment puis-je cultiver plus de gratitude et d'appréciation ?",
    "Quels sont mes plus beaux souvenirs de la personne que j'ai perdue ?",
    "Quelles sont les choses que j'aurais voulu dire ou faire avec cette personne avant qu'elle disparaisse ?",
    "Quelle est la chose la plus difficile dans le fait de faire face à cette perte ?",
    "Comment puis-je trouver des façons de faire face à mon deuil ?",
    "Comment cette perte a-t-elle impacté ma routine quotidienne ?",
    "Quelles sont les choses que j'ai apprises sur moi-même ou sur la vie en général à la suite de cette perte ?",
    "Quelles sont certaines étapes positives que je peux prendre pour honorer la mémoire de la personne que j'ai perdue ?",
    "Comment puis-je trouver du soutien et du réconfort pendant cette période difficile ?",
    "Qui sont les personnes dans ma vie vers qui je peux me tourner pour du soutien et de l'affection alors que je traverse mon deuil ?",
    "Quelles sont certaines façons saines de traiter mon deuil, comme à travers l'exercice, la méditation, ou des exutoires créatifs comme l'art ou la musique ?",
    "Qu'est-ce qui se passe en ce moment qui rend cette période si difficile ?",
    "Qu'est-ce qui cause ma détresse ?",
    "Vers qui puis-je me tourner pour du soutien ?",
    "Comment ai-je fait face aux moments difficiles dans le passé ?",
    "Quelles sont certaines choses pour lesquelles je suis reconnaissant(e), même dans des circonstances difficiles ?",
    "Comment puis-je cultiver un sentiment d'appréciation et d'optimisme face à l'adversité ?",
    "Quelles pratiques d'auto-soin m'ont aidé(e) dans le passé ?",
    "Que puis-je apprendre de cette expérience ? Quelles leçons pourrais-je en tirer ?",
    "Comment puis-je recadrer la situation ?",
    "Quelles actions puis-je prendre pour améliorer la situation ?",
    "Quelles sont les choses positives que j'ai dans ma vie en ce moment ?",
    "Que puis-je faire pour prendre soin de moi en ce moment ?",
    "Quelles sont mes valeurs et croyances personnelles ? Comment façonnent-elles mon identité ?",
    "Quels sont certains des rôles que j'assume dans ma vie ? Comment ces rôles contribuent-ils à mon sentiment d'identité ?",
    "Comment est-ce que je me définis en termes de relations avec les autres ? Comment ces relations façonnent-elles mon sens de moi-même ?",
    "Que sais-je de mon environnement culturel ou ethnique ? Comment mon environnement culturel ou ethnique façonne-t-il mon identité ?",
    "Quelles sont certaines des forces, des talents ou des qualités uniques que je possède ? Comment cela me défini-t-il ?",
    "Comment mon apparence physique façonne-t-elle mon sentiment d'identité ?",
    "Quelles expériences de vie m'ont façonné(e) tel(le) que je suis aujourd'hui ?",
    "Quelles sont certaines des peurs ou des doutes que j'ai sur mon identité ? Comment puis-je aborder ces peurs ou ces doutes de manière saine ?",
    "Comment est-ce que j'équilibre mon besoin d'individualité avec mon besoin d'un sentiment de communauté ou d'appartenance ?",
    "Quelles sont certaines des choses que je veux accomplir dans la vie ? Comment ces objectifs contribuent-ils à mon sentiment d'identité ?",
    "Quel est l'un de mes premiers souvenirs d'enfance ?",
    "Quelles émotions ce souvenir évoque-t-il ?",
    "Quel est un souvenir heureux de mon enfance ? Qu'est-ce qui le rend si spécial ?",
    "Quel est un souvenir difficile de mon passé ? Comment ce souvenir m'a-t-il façonné(e) en tant que personne ?",
    "Qui étaient certains de mes amis les plus proches en grandissant ? Quel impact ont-ils eu sur ma vie ?",
    "Qui étaient certains de mes modèles ou mentors en grandissant ? Quel impact ont-ils eu sur ma vie ?",
    "Quels étaient certains de mes loisirs ou activités préférés en grandissant ? Est-ce que j'en profite encore aujourd'hui ?",
    "Quels étaient certains des jalons ou accomplissements majeurs que j'ai atteints dans ma vie ? Comment m'ont-ils fait sentir ?",
    "Quelles étaient certaines des expériences les plus difficiles ou transformatrices que j'ai vécues dans ma vie ? Comment ont-elles façonné ma perspective ou mes valeurs ?",
    "Quelles étaient certaines des plus grandes surprises ou tournants inattendus que ma vie a pris ? Comment ai-je fait face à ces changements ?",
    "Quelles étaient certaines des personnes ou expériences qui m'ont apporté le plus de joie ou de sens dans ma vie ? Comment puis-je cultiver plus de ces influences positives dans mon présent ?",
    "Quels sont mes loisirs ou activités préférés ?",
    "Comment mes loisirs ou activités préférés me font-ils sentir ?",
    "Si j'avais tout le temps et toutes les ressources dont j'avais besoin, quelles activités ou loisirs poursuivrais-je ?",
    "Qu'est-ce que j'aime le plus dans mon loisir préféré ? Comment puis-je en intégrer davantage dans ma vie ?",
    "Qui est-ce que je connais qui partage ma passion ou mon loisir, et comment pouvons-nous collaborer ou nous soutenir mutuellement ?",
    "Quelles compétences est-ce que je possède qui pourraient être appliquées à un nouveau loisir ou activité ?",
    "Quelle est une chose que j'ai toujours voulu essayer mais que je n'ai pas encore faite, et qu'est-ce qui me retient ?",
    "Si je pouvais transformer ma passion ou mon loisir en carrière ou en activité secondaire, quelles étapes pourrais-je prendre pour y parvenir ?",
    "De quoi ai-je peur ?",
    "Quelle est la source de ma peur ? D'où vient-elle ?",
    "Comment ma peur affecte-t-elle ma vie ? Dans quelle mesure me retient-elle ?",
    "À quoi ressemblerait ma vie sans cette peur ? Qu'est-ce que je pourrais accomplir ou vivre ?",
    "Comment puis-je recadrer ma peur ? Y a-t-il une façon de voir la situation ou le problème différemment ?",
    "Quelles étapes puis-je prendre pour faire face à ma peur ? Quelle action puis-je prendre pour la traverser ?",
    "Vers qui puis-je me tourner pour du soutien ? Qui peut m'aider à affronter ma peur ?",
    "Qu'ai-je appris des expériences passées de faire face à la peur ? Qu'est-ce qui a bien fonctionné et qu'est-ce qui n'a pas fonctionné ?",
    "Comment puis-je utiliser ma peur comme motivation ? Puis-je transformer ma peur en une force positive qui me fait avancer ?",
    "Quel est le pire qui puisse arriver si j'affronte ma peur ? Quel est le meilleur qui puisse arriver ?",
    "Quelles sont certaines peurs ou croyances limitantes qui me retiennent ?",
    "Comment puis-je travailler à les surmonter ?",
    "Quelles ressources ou quel soutien puis-je chercher pour m'aider à surmonter mes peurs ?",
    "Quelle émotion est-ce que je ressens en ce moment ? Note toutes les émotions qui te viennent à l'esprit, aussi grandes ou petites qu'elles soient.",
    "Où est-ce que je ressens cette émotion dans mon corps ? Quelles sont les sensations physiques que j'éprouve quand je ressens cette émotion ? Se manifeste-t-elle dans une certaine partie de mon corps ou d'une certaine façon ?",
    "Qu'est-ce qui a déclenché cette émotion ? Était-ce une pensée, un souvenir, ou quelque chose que quelqu'un a dit ou fait ?",
    "Comment est-ce que je réponds à cette émotion ?",
    "Quand ai-je ressenti cela pour la dernière fois ?",
    "Quelles émotions est-ce que je ressens le plus souvent ?",
    "Quelles émotions est-ce que j'évite de ressentir ?",
    "Comment mes émotions ont-elles affecté mes pensées et mon comportement aujourd'hui ?",
    "Comment puis-je exprimer cette émotion de manière saine ?",
    "Que puis-je apprendre de cette émotion ? Réfléchis à la façon dont cette émotion peut t'apprendre quelque chose sur toi-même, tes valeurs ou tes besoins.",
    "Quels ont été certains moments de stress ou de frustration aujourd'hui ?",
    "Quels ont été certains moments de paix ou de calme aujourd'hui ?",
    "Comment ai-je géré les émotions négatives aujourd'hui ?",
    "Comment puis-je mieux faire face aux émotions difficiles à l'avenir ?",
    "Quelles sont certaines façons dont je peux favoriser la positivité et le bonheur dans ma vie ?",
    "Comment puis-je me soutenir à travers cette émotion ? Note des stratégies d'auto-soin qui peuvent t'aider à te sentir plus ancré(e) et centré(e) lorsque tu vis cette émotion.",
    "Que se passe-t-il en ce moment présent ?",
    "Quelles sont cinq choses que je peux voir en ce moment, et quelles couleurs, formes et textures ont-elles ?",
    "Si mon esprit était comme l'océan en ce moment, comment est l'eau ?",
    "Quelles pensées est-ce que j'observe en ce moment ?",
    "Quelles informations sensorielles est-ce que je reçois en ce moment présent ?",
    "Quelles sont trois choses que je peux entendre en ce moment, et comment sonnent-elles ?",
    "Quelles sont trois choses que je peux ressentir physiquement en ce moment, comme le poids de mon corps sur une chaise ou la texture de mes vêtements ?",
    "Quelles sont trois choses que je peux sentir en ce moment, et comment sentent-elles ?",
    "Quelles sont trois choses que je peux goûter en ce moment, et quel goût ont-elles ?",
    "Quelles émotions est-ce que je ressens en ce moment, et comment puis-je pratiquer l'acceptation et l'auto-compassion envers elles ?",
    "Quelles pensées traversent mon esprit en ce moment, et comment puis-je les reconnaître sans me laisser emporter par elles ?",
    "Quelles sont trois choses que j'attends avec impatience dans la prochaine heure, et comment puis-je rester présent(e) et ouvert(e) à les vivre pleinement ?",
    "Quelles sont trois choses qui m'inquiètent en ce moment, et comment puis-je pratiquer la pleine conscience pour réduire mon stress et mon anxiété ?",
    "Quelles sont trois petites actions que je peux prendre en ce moment pour me ramener dans le moment présent, comme prendre une grande respiration, m'étirer, ou savourer une gorgée de thé ou de café ?",
    "Qu'est-ce qui est dans mon esprit ce matin ?",
    "À quoi est-ce que j'aspire aujourd'hui ?",
    "Que dois-je faire aujourd'hui ?",
    "Quels sont mes objectifs pour aujourd'hui ?",
    "Quelles sont certaines façons dont je peux être productif(ve) aujourd'hui ?",
    "Que puis-je faire aujourd'hui pour prendre soin de ma santé physique et mentale ?",
    "Quels sont certains défis que je pourrais affronter aujourd'hui et comment puis-je m'y préparer ?",
    "Comment puis-je prioriser l'auto-soin aujourd'hui ?",
    "Vers qui puis-je me tourner pour du soutien aujourd'hui ?",
    "Quelle est une chose que je peux faire aujourd'hui pour aider quelqu'un d'autre ?",
    "Quels sont certains de mes souvenirs et expériences les plus mémorables et significatifs ? Comment peuvent-ils m'inspirer à aller de l'avant ?",
    "Comment puis-je embrasser le changement et les nouvelles opportunités dans ma vie ?",
    "Quelles sont certaines choses qui me font me sentir confiant(e) ?",
    "Comment ai-je surmonté des défis dans le passé, et qu'ai-je appris de ces expériences ?",
    "Quelle est une chose que je peux faire aujourd'hui pour sortir de ma zone de confort et renforcer ma confiance ?",
    "Quels sont certains schémas de pensée négative dans lesquels je m'engage, et comment puis-je recadrer ces pensées de manière plus positive ?",
    "Quelles sont mes forces et comment puis-je les utiliser pour atteindre mes objectifs ?",
    "Quels sont certains compliments que les autres m'ont faits dans le passé, et comment puis-je intérioriser ces messages positifs ?",
    "Comment puis-je prendre soin de moi et pratiquer l'auto-compassion dans les moments où je me sens incertain(e) ou dans le doute ?",
    "Que dirais-je à un(e) ami(e) qui a du mal avec la confiance en soi, et comment puis-je appliquer ce conseil à ma propre vie ?",
    "Comment puis-je embrasser mes qualités uniques et les utiliser à mon avantage ?",
    "Quelle est une étape que je peux prendre aujourd'hui pour travailler vers un objectif qui renforcera ma confiance en moi ?",
    "Quelles sont mes qualités et forces uniques, et comment puis-je les embrasser et les célébrer plus pleinement ?",
    "Quelles sont trois choses que j'ai accomplies cette semaine dont je suis fier/fière ?",
    "Comment puis-je être plus gentil(le) envers moi-même aujourd'hui ?",
    "Quelles sont mes forces uniques et comment m'ont-elles aidé(e) dans le passé ?",
    "Quelle est une pensée négative que j'ai sur moi-même que je peux remettre en question avec une pensée positive ?",
    "Que puis-je faire pour prendre soin de moi physiquement et émotionnellement aujourd'hui ?",
    "Quelles sont trois choses que j'aime chez moi ?",
    "Comment ai-je grandi et changé en tant que personne au cours de l'année écoulée ?",
    "Quelle est une affirmation positive que je peux me répéter tout au long de la journée ?",
    "Quelle est une petite étape que je peux prendre aujourd'hui pour travailler vers un objectif ou un rêve personnel ?",
    "Quelles sont certaines valeurs qui sont importantes pour moi, et comment guident-elles mes décisions et actions ?",
    "Quelles sont certaines expériences de mon passé qui m'ont façonné(e) tel(le) que je suis aujourd'hui, et comment ont-elles influencé mes croyances et attitudes ?",
    "Quelles sont certaines choses qui me procurent de la joie et de la satisfaction, et comment puis-je en intégrer davantage dans ma vie ?",
    "Quels sont certains schémas de comportement ou de pensée qui me retiennent, et comment puis-je travailler à briser ces schémas ?",
    "Quels sont certains objectifs ou aspirations que j'ai pour ma vie, et quelles étapes puis-je prendre pour y travailler ?",
    "Quelles sont certaines peurs ou insécurités qui me retiennent, et comment puis-je travailler à les surmonter ?",
    "Quelles sont certaines relations qui sont importantes pour moi, et comment puis-je les nourrir et les renforcer ?",
    "Quelles sont certaines erreurs ou échecs de mon passé qui m'ont appris des leçons précieuses, et comment puis-je appliquer ces leçons à ma vie actuelle ?",
    "Quelles sont certaines pratiques d'auto-soin qui sont importantes pour moi, et comment puis-je en faire une partie régulière de ma routine ?",
    "Quelles sont certaines choses pour lesquelles je suis reconnaissant(e) dans ma vie, et comment puis-je cultiver plus de gratitude au quotidien ?",
    "Qu'est-ce qui a déclenché des sentiments négatifs aujourd'hui ?",
    "Comment pense-je que les autres me perçoivent ?",
    "Qu'est-ce que les autres m'ont communiqué sur moi-même ?",
    "Comment est-ce que je réponds aux compliments ?",
    "Quand est-ce que je me sens valorisé(e) et aimé(e) ?",
    "Quels défis ai-je affrontés en tant qu'enfant ?",
    "Quels sont mes meilleurs et pires traits ?",
    "Pour quoi dois-je me pardonner ?",
    "Pour quoi est-ce que je juge les autres, et pourquoi ?",
    "Est-ce que je ressens de la culpabilité ou de la honte pour quelque chose ?",
    "Comment est-ce que je soutiens les autres, et est-ce que je me montre le même amour ?",
    "Qu'est-ce que je considère comme des limites saines ?",
    "Quand est-ce que j'éprouve le besoin de mentir, et quel est le pire mensonge que j'ai dit ?",
    "Quelles parties de moi-même est-ce que je cache ?",
    "Que signifie la spiritualité pour moi ?",
    "Quel rôle joue la spiritualité dans ma vie quotidienne ?",
    "Quels livres, enseignements ou leaders spirituels m'ont influencé(e) ? Qu'ai-je appris de ces sources ?",
    "Comment puis-je intégrer mes croyances et pratiques spirituelles dans mes routines ?",
    "Comment est-ce que je définis mes croyances et valeurs ?",
    "Comment mes croyances et valeurs ont-elles évolué avec le temps ?",
    "Comment est-ce que je me connecte à une puissance supérieure ou au divin ?",
    "Quelles pratiques ou rituels est-ce que je trouve utiles pour nourrir ma spiritualité ?",
    "Comment puis-je incorporer plus de spiritualité dans ma vie quotidienne ?",
    "Comment puis-je explorer ma relation avec le divin ou la puissance supérieure ?",
    "Quelles questions ou incertitudes ai-je sur ma spiritualité ? Comment puis-je explorer ces questions et chercher des réponses ?",
    "Comment puis-je utiliser ma spiritualité pour cultiver un sens de la compassion et de l'empathie envers les autres, et contribuer au bien commun de l'humanité ?",
    "Quelles sont certaines des sources de stress dans ma vie en ce moment ?",
    "Comment ai-je fait face au stress dans le passé ?",
    "Quels sont certains mécanismes d'adaptation sains que je peux utiliser pour gérer le stress ?",
    "Comment puis-je prioriser l'auto-soin pour réduire le stress ?",
    "Quelles sont certaines affirmations positives que je peux me dire pour combattre le stress ?",
    "Vers qui puis-je me tourner pour du soutien et de l'encouragement quand je me sens stressé(e) ?",
    "Comment puis-je recadrer les pensées négatives et maintenir une perspective positive ?",
    "Quelles sont certaines activités ou passe-temps qui m'aident à me détendre et à décompresser ?",
    "Comment puis-je créer un environnement sans stress à la maison ou au travail ?",
    "Quelles sont certaines étapes que je peux prendre pour éviter que le stress ne m'envahisse à l'avenir ?",
    "Quelles sont certaines solutions pratiques aux sources de stress dans ma vie ?",
    "Comment puis-je prioriser mon temps et mes responsabilités pour réduire le stress ?",
    "Quelles sont certaines activités physiques que je peux faire pour soulager le stress ?",
    "Comment puis-je maintenir un équilibre sain entre vie professionnelle et vie privée pour réduire le stress ?",
    "Comment puis-je rester organisé(e) et sur la bonne voie pour réduire le stress ?",
    "Comment puis-je trouver de l'humour et de la joie dans la vie pour combattre le stress ?",
    "Quels sont certains exercices de réflexion que je peux faire pour réduire le stress ?",
    "Comment puis-je maintenir un mode de vie sain pour réduire le stress, comme bien manger, dormir suffisamment et faire de l'exercice régulièrement ?",
    "Comment puis-je fixer des attentes et des limites réalistes pour réduire le stress ?",
    "Quelles sont certaines choses que je peux faire pour maintenir un état d'esprit positif et détendu, comme méditer, pratiquer la pleine conscience, ou passer du temps dans la nature ?",
    "Où est-ce que je voyage actuellement et quelles sont mes attentes pour ce voyage ?",
    "Quelles sont certaines nouvelles choses que je veux vivre et essayer pendant ce voyage ?",
    "Quelles sont certaines choses que je veux apprendre ou mieux comprendre sur la culture et les gens dans les endroits que je visite ?",
    "Comment me suis-je senti(e) en arrivant à ma destination ? Quelles ont été mes premières impressions ?",
    "Qu'ai-je fait le premier jour de voyage ? Quels ont été les moments forts ?",
    "Quelles sont certaines choses que je veux faire ou voir pendant que je suis ici ?",
    "Qu'ai-je fait aujourd'hui ? Quels ont été les moments forts ?",
    "Qu'ai-je appris sur l'endroit que je visite aujourd'hui ?",
    "Quelles sont certaines personnes intéressantes que j'ai rencontrées ? Qu'ai-je appris d'elles ?",
    "Quelles impressions ai-je tirées de l'endroit que je visite ?",
    "Qu'est-ce qui est beau ou unique dans l'endroit que je visite ?",
    "Quel a été le moment le plus mémorable de mon voyage jusqu'à présent, et pourquoi ?",
    "Quelles merveilles naturelles ai-je vues aujourd'hui ? Comment m'ont-elles fait sentir ?",
    "Me suis-je engagé(e) dans des activités de plein air aujourd'hui ? Lesquelles, et comment m'ont-elles défié(e) ou inspiré(e) ?",
    "Quelles flore ou faune locales ai-je rencontrées aujourd'hui ? Qu'ai-je appris à leur sujet ?",
    "Ai-je pris du temps pour me détendre aujourd'hui ? Comment ai-je passé ce temps ?",
    "Comment est-ce que je me sens par rapport à mon voyage jusqu'à présent ? Quelles sont certaines choses qui m'ont surpris(e) ?",
    "Quelles sont certaines nouvelles choses que je veux essayer avant la fin de mon voyage ?",
    "Qu'ai-je appris sur moi-même lors de ce voyage ?",
    "Pour quoi suis-je le plus reconnaissant(e) lors de ce voyage ?",
    "Quels défis ai-je affrontés pendant mes voyages, et comment les ai-je surmontés ?",
    "Quelles sont certaines choses que je ferais différemment si je pouvais refaire ce voyage ?",
    "Quelles sont certaines choses qui me manqueront le plus dans cet endroit ?",
    "Qui ai-je rencontré lors de ce voyage qui m'a marqué(e), et qu'ai-je appris de cette personne ?",
    "Quelles sont certaines observations ou réflexions intéressantes que j'ai eues sur les endroits que j'ai visités ?",
    "Qu'ai-je appris sur moi-même pendant mes voyages, et comment cette expérience m'a-t-elle changé(e) ?",
    "Quelles sont certaines façons dont je peux prendre les leçons et les expériences de mes voyages et les appliquer à ma vie à la maison ?",
    "Et si j'avais le pouvoir de voler ? Comment utiliserais-je cette capacité, et où irais-je ?",
    "Et si je pouvais vivre n'importe où dans le monde ? Où choisirais-je, et pourquoi ?",
    "Et si je gagnais à la loterie ? Comment ma vie changerait-elle, et que ferais-je avec l'argent ?",
    "Et si je pouvais échanger ma place avec quelqu'un pour une journée ? Qui choisirais-je, et que ferais-je à sa place ?",
    "Et si je pouvais rencontrer n'importe quelle personne célèbre, vivante ou morte ? Qui choisirais-je, et que lui demanderais-je ?",
    "Et si je pouvais parler couramment n'importe quelle langue ? Quelle langue choisirais-je, et que ferais-je avec cette compétence ?",
    "Et si je pouvais revivre n'importe quel jour de mon passé ? Quel jour choisirais-je, et que ferais-je différemment ?",
    "Et si je pouvais parler à n'importe quel animal ? Quel animal choisirais-je, et que lui demanderais-je ?",
    "Et si j'avais pris une décision charnière différente dans mon passé ? Quelle décision aurait changé le cours de ma vie ?",
]

# ── Journal State ───────────────────────────────────────────────────────────

def ensure_journal_dir():
    os.makedirs(JOURNAL_DIR, exist_ok=True)

def today_str():
    return datetime.now().strftime("%Y-%m-%d")

def entry_exists(date_str):
    """Check if any journal entry exists for a given date."""
    ensure_journal_dir()
    return any(f.startswith(date_str) and f.endswith(FILE_EXT)
               for f in os.listdir(JOURNAL_DIR))

def entry_count_today():
    """Count how many entries exist for today."""
    ensure_journal_dir()
    ds = today_str()
    return sum(1 for f in os.listdir(JOURNAL_DIR)
               if f.startswith(ds) and f.endswith(FILE_EXT))

def list_entries():
    """Return list of entry filenames, newest first."""
    ensure_journal_dir()
    files = [f for f in os.listdir(JOURNAL_DIR)
             if f.endswith(FILE_EXT) and not f.startswith(".")]
    files.sort(reverse=True)
    return files

def read_entry(filename):
    """Read an entry's contents. Returns text or None."""
    try:
        with open(os.path.join(JOURNAL_DIR, filename), 'r', errors='replace') as f:
            return f.read()
    except Exception:
        return None

def get_week_dates():
    """Get Monday–Sunday dates for the current week."""
    today = datetime.now().date()
    monday = today - timedelta(days=today.weekday())
    return [monday + timedelta(days=i) for i in range(7)]

def get_streak():
    """Count consecutive days with entries ending at yesterday or today."""
    today = datetime.now().date()
    streak = 0
    day = today
    while True:
        if entry_exists(day.strftime("%Y-%m-%d")):
            streak += 1
            day -= timedelta(days=1)
        else:
            break
    return streak

def get_total_entries():
    """Count total journal entries."""
    ensure_journal_dir()
    return len([f for f in os.listdir(JOURNAL_DIR)
                if f.endswith(FILE_EXT) and not f.startswith(".")])

def save_entry(text):
    """Save a journal entry as plain text."""
    ensure_journal_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filepath = os.path.join(JOURNAL_DIR, f"{timestamp}{FILE_EXT}")
    with open(filepath, 'w') as f:
        f.write(text)
    return filepath

# ── UI Components ───────────────────────────────────────────────────────────

def draw_status(stdscr, left="", right="", style=None):
    h, w = stdscr.getmaxyx()
    if style is None:
        style = curses.A_REVERSE
    bar = left + " " * max(0, w - len(left) - len(right)) + right
    bar = bar[:w]
    try:
        stdscr.addstr(h - 1, 0, bar, style)
    except curses.error:
        pass

def draw_help_bar(stdscr, text):
    h, w = stdscr.getmaxyx()
    text = text[:w]
    try:
        stdscr.addstr(h - 2, 0, text + " " * max(0, w - len(text)), curses.A_DIM)
    except curses.error:
        pass

def prompt_input(stdscr, label):
    """Prompt for text input. Returns string or None on Esc."""
    curses.curs_set(1)
    h, w = stdscr.getmaxyx()
    buf = ""
    while True:
        display = f" {label}{buf}"
        try:
            stdscr.addstr(h - 1, 0, display + " " * max(0, w - len(display)),
                          curses.A_REVERSE)
            stdscr.move(h - 1, min(len(display), w - 1))
        except curses.error:
            pass
        stdscr.refresh()

        try:
            ch = stdscr.get_wch()
        except curses.error:
            continue
        if ch == 27:
            curses.curs_set(0)
            return None
        elif ch in (curses.KEY_ENTER, '\n', '\r'):
            curses.curs_set(0)
            return buf.strip()
        elif ch in (curses.KEY_BACKSPACE, '\x7f', '\x08'):
            buf = buf[:-1]
        elif isinstance(ch, str) and ch >= ' ':
            buf += ch

def confirm(stdscr, message):
    """Yes/no confirmation."""
    h, w = stdscr.getmaxyx()
    draw_status(stdscr, left=f" {message} (y/n)")
    stdscr.refresh()
    while True:
        ch = stdscr.getch()
        if ch in (ord('y'), ord('Y')):
            return True
        if ch in (ord('n'), ord('N'), 27):
            return False

# ── Word Wrap ───────────────────────────────────────────────────────────────

def wrap_line(line, width):
    if width <= 0:
        return [(0, len(line))]
    if len(line) == 0:
        return [(0, 0)]
    segments = []
    pos = 0
    length = len(line)
    while pos < length:
        if length - pos <= width:
            segments.append((pos, length))
            break
        chunk_end = pos + width
        break_at = line.rfind(' ', pos, chunk_end)
        if break_at > pos:
            segments.append((pos, break_at))
            pos = break_at + 1
        else:
            segments.append((pos, chunk_end))
            pos = chunk_end
    return segments

def build_wrap_map(lines, width):
    vrows = []
    for li, line in enumerate(lines):
        segs = wrap_line(line, width)
        for start, end in segs:
            vrows.append((li, start, end))
    return vrows

def logical_to_visual(vrows, cy, cx):
    for vi, (li, scol, ecol) in enumerate(vrows):
        if li == cy and scol <= cx <= ecol:
            if cx == ecol and ecol > scol:
                if vi + 1 < len(vrows) and vrows[vi + 1][0] == li:
                    continue
            return vi, cx - scol
    if vrows:
        vi = len(vrows) - 1
        li, scol, ecol = vrows[vi]
        return vi, min(cx - scol, ecol - scol)
    return 0, 0

def visual_to_logical(vrows, vi, screen_cx):
    if not vrows:
        return 0, 0
    vi = max(0, min(vi, len(vrows) - 1))
    li, scol, ecol = vrows[vi]
    max_cx = ecol - scol
    screen_cx = max(0, min(screen_cx, max_cx))
    return li, scol + screen_cx

def word_count(lines):
    return sum(len(line.split()) for line in lines)

# ── Main Screen ─────────────────────────────────────────────────────────────

def draw_main_screen(stdscr, accent):
    """Draw the journal home screen with weekly tracker."""
    curses.curs_set(0)

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        week_dates = get_week_dates()
        today = datetime.now().date()
        today_count = entry_count_today()
        streak = get_streak()
        total = get_total_entries()

        # Title
        row = 1
        title = "Journal"
        tx = max(0, (w - len(title)) // 2)
        try:
            stdscr.addstr(row, tx, title, curses.A_BOLD)
        except curses.error:
            pass

        # Weekly tracker
        row = 4
        day_names = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]

        header = "  "
        marks = "  "
        for i, d in enumerate(week_dates):
            dstr = d.strftime("%Y-%m-%d")
            is_today = (d == today)
            has_entry = entry_exists(dstr)

            name = day_names[i]
            if is_today:
                header += f"[{name}]"
            else:
                header += f" {name} "
            if i < 6:
                header += "  "

            if has_entry:
                marks += "  ✓  "
            elif d <= today:
                marks += "  ·  "
            else:
                marks += "     "
            if i < 6:
                marks += "  "

        hx = max(0, (w - len(header)) // 2)
        mx = max(0, (w - len(marks)) // 2)
        try:
            stdscr.addstr(row, hx, header, accent)
            stdscr.addstr(row + 1, mx, marks, curses.A_BOLD)
        except curses.error:
            pass

        # Stats
        row = 8
        stats = f"Série : {streak} jour{'s' if streak != 1 else ''}  ·  Total : {total} entrée{'s' if total != 1 else ''}"
        sx = max(0, (w - len(stats)) // 2)
        try:
            stdscr.addstr(row, sx, stats, curses.A_DIM)
        except curses.error:
            pass

        # Today's status
        row = 10
        if today_count > 0:
            if today_count == 1:
                status = "✓ 1 entrée aujourd'hui"
            else:
                status = f"✓ {today_count} entrées aujourd'hui"
            style = accent | curses.A_BOLD
        else:
            status = "Aucune entrée aujourd'hui"
            style = curses.A_DIM
        stx = max(0, (w - len(status)) // 2)
        try:
            stdscr.addstr(row, stx, status, style)
        except curses.error:
            pass

        # Menu — always visible
        row = 13
        opt1 = "[G] Écriture guidée"
        opt2 = "[F] Écriture libre"
        opt3 = "[H] Historique"
        o1x = max(0, (w - len(opt1)) // 2)
        o2x = max(0, (w - len(opt2)) // 2)
        o3x = max(0, (w - len(opt3)) // 2)
        try:
            stdscr.addstr(row, o1x, opt1)
            stdscr.addstr(row + 1, o2x, opt2)
            if total > 0:
                stdscr.addstr(row + 2, o3x, opt3)
        except curses.error:
            pass

        quit_opt = "[Q] Quitter"
        qx = max(0, (w - len(quit_opt)) // 2)
        try:
            stdscr.addstr(row + 4, qx, quit_opt, curses.A_DIM)
        except curses.error:
            pass

        stdscr.refresh()
        ch = stdscr.getch()

        if ch == ord('q'):
            return None

        elif ch == ord('g'):
            return "prompt"

        elif ch == ord('f'):
            return "freewrite"

        elif ch == ord('h') and total > 0:
            return "view"

# ── Entry Browser & Viewer ──────────────────────────────────────────────────

def entry_browser(stdscr, accent):
    """Browse past entries. Returns filename to view, or None."""
    curses.curs_set(0)
    sel = 0
    scroll_off = 0

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        usable = h - 3

        entries = list_entries()

        header = " Historique du journal"
        try:
            stdscr.addstr(0, 0, (header + " " * w)[:w], curses.A_BOLD)
        except curses.error:
            pass

        if not entries:
            msg = "Aucune entrée pour l'instant."
            try:
                stdscr.addstr(h // 2, max(0, (w - len(msg)) // 2), msg, curses.A_DIM)
            except curses.error:
                pass
        else:
            sel = max(0, min(sel, len(entries) - 1))
            if sel < scroll_off:
                scroll_off = sel
            if sel >= scroll_off + usable:
                scroll_off = sel - usable + 1

            for i in range(usable):
                idx = scroll_off + i
                if idx >= len(entries):
                    break
                fname = entries[idx]
                # Parse date from filename: 2026-03-27_143022.txt
                date_part = fname.replace(FILE_EXT, '')
                try:
                    dt = datetime.strptime(date_part, "%Y-%m-%d_%H%M%S")
                    MOIS_FR = ["jan", "fév", "mar", "avr", "mai", "juin",
                               "juil", "août", "sep", "oct", "nov", "déc"]
                    display_date = f"{dt.day:02d} {MOIS_FR[dt.month - 1]} {dt.year}  {dt.strftime('%H:%M')}"
                except ValueError:
                    display_date = date_part

                # Read first line of content for preview
                content = read_entry(fname)
                preview = ""
                if content:
                    # Skip metadata header to find actual writing
                    for line in content.split('\n'):
                        stripped = line.strip()
                        if stripped and not stripped.startswith(('DATE:', 'WORDS:', 'PROMPT:', 'FREEWRITE')):
                            preview = stripped[:w - len(display_date) - 10]
                            break
                    if not preview:
                        lines = [l.strip() for l in content.split('\n') if l.strip()]
                        if lines:
                            preview = lines[0][:w - len(display_date) - 10]

                row = i + 1
                if idx == sel:
                    style = curses.A_REVERSE
                    prefix = " › "
                else:
                    style = curses.A_NORMAL
                    prefix = "   "

                line = prefix + display_date
                if preview:
                    remaining = w - len(line) - 3
                    if remaining > 10:
                        line += "  " + preview[:remaining]
                line = line[:w]
                try:
                    stdscr.addstr(row, 0, line + " " * max(0, w - len(line)), style)
                except curses.error:
                    pass

        help_text = " [Entrée] Lire  [S] Supprimer  [Q] Quitter"
        try:
            stdscr.addstr(h - 2, 0, (help_text + " " * w)[:w], curses.A_DIM)
        except curses.error:
            pass

        count = f"{len(entries)} entrée{'s' if len(entries) != 1 else ''}"
        draw_status(stdscr, left=" ~/journal", right=f"{count} ")

        stdscr.refresh()
        ch = stdscr.getch()

        if ch == ord('q') or ch == 27:
            return None
        elif ch == curses.KEY_UP or ch == ord('k'):
            sel = max(0, sel - 1)
        elif ch == curses.KEY_DOWN or ch == ord('j'):
            sel = min(max(0, len(entries) - 1), sel + 1)
        elif ch == curses.KEY_HOME:
            sel = 0
        elif ch == curses.KEY_END:
            sel = max(0, len(entries) - 1)
        elif ch in (curses.KEY_ENTER, 10, 13):
            if entries:
                return entries[sel]
        elif ch == ord('s'):
            if entries:
                fname = entries[sel]
                date_part = fname.replace(FILE_EXT, '')
                try:
                    dt = datetime.strptime(date_part, "%Y-%m-%d_%H%M%S")
                    MOIS_FR = ["jan", "fév", "mar", "avr", "mai", "juin",
                               "juil", "août", "sep", "oct", "nov", "déc"]
                    label = f"{MOIS_FR[dt.month - 1]} {dt.day:02d} {dt.year} {dt.strftime('%H:%M')}"
                except ValueError:
                    label = fname
                if confirm(stdscr, f"supprimer l'entrée du {label} ?"):
                    try:
                        os.remove(os.path.join(JOURNAL_DIR, fname))
                    except Exception:
                        pass
                    sel = max(0, sel - 1)


def entry_viewer(stdscr, accent, filename):
    """Read-only pager for a journal entry."""
    curses.curs_set(0)

    content = read_entry(filename)
    if not content:
        return

    h, w = stdscr.getmaxyx()

    # Parse date for header
    date_part = filename.replace(FILE_EXT, '')
    try:
        dt = datetime.strptime(date_part, "%Y-%m-%d_%H%M%S")
        MOIS_FR = ["jan", "fév", "mar", "avr", "mai", "juin",
                   "juil", "août", "sep", "oct", "nov", "déc"]
        display_date = f"{dt.day:02d} {MOIS_FR[dt.month - 1]} {dt.year}  {dt.strftime('%H:%M')}"
    except ValueError:
        display_date = date_part

    # Build display lines
    lines = []
    lines.append({"text": "", "style": curses.A_NORMAL})
    lines.append({"text": f"  {display_date}", "style": accent | curses.A_BOLD})
    lines.append({"text": "", "style": curses.A_NORMAL})

    for raw_line in content.split('\n'):
        stripped = raw_line.strip()
        # Style metadata differently
        if stripped.startswith(('DATE:', 'WORDS:')):
            continue  # skip metadata, we show date in header
        elif stripped.startswith('PROMPT:'):
            prompt_text = stripped[7:].strip()
            wrapped = textwrap.fill(prompt_text, width=w - 6)
            for wl in wrapped.split('\n'):
                lines.append({"text": f"  {wl}", "style": accent | curses.A_DIM})
            lines.append({"text": "", "style": curses.A_NORMAL})
        elif stripped == 'FREEWRITE':
            lines.append({"text": "  écriture libre", "style": curses.A_DIM})
            lines.append({"text": "", "style": curses.A_NORMAL})
        elif stripped == '':
            lines.append({"text": "", "style": curses.A_NORMAL})
        else:
            wrapped = textwrap.fill(raw_line, width=w - 4)
            for wl in wrapped.split('\n'):
                lines.append({"text": f"  {wl}", "style": curses.A_NORMAL})

    lines.append({"text": "", "style": curses.A_NORMAL})

    scroll = 0

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        text_h = h - 2
        max_scroll = max(0, len(lines) - text_h)
        scroll = max(0, min(scroll, max_scroll))

        for i in range(text_h):
            line_idx = scroll + i
            if line_idx >= len(lines):
                break
            ld = lines[line_idx]
            try:
                stdscr.addstr(i, 0, ld["text"][:w - 1], ld.get("style", curses.A_NORMAL))
            except curses.error:
                pass

        # Status bar
        if len(lines) > text_h:
            pct = int((scroll / max(1, max_scroll)) * 100)
            pos = f" {pct}%"
        else:
            pos = " 100%"
        draw_status(stdscr, left=f" {display_date}  (lecture seule)", right=f"{pos} ")

        help_text = " ↑↓ défiler  g/G début/fin  q:retour"
        try:
            stdscr.addstr(h - 2, 0, (help_text + " " * w)[:w], curses.A_DIM)
        except curses.error:
            pass

        stdscr.refresh()
        ch = stdscr.getch()

        if ch == ord('q') or ch == 27:
            return
        elif ch == curses.KEY_UP or ch == ord('k'):
            scroll = max(0, scroll - 1)
        elif ch == curses.KEY_DOWN or ch == ord('j'):
            scroll = min(max_scroll, scroll + 1)
        elif ch == curses.KEY_PPAGE or ch == ord(' '):
            scroll = max(0, scroll - text_h)
        elif ch == curses.KEY_NPAGE:
            scroll = min(max_scroll, scroll + text_h)
        elif ch == ord('g'):
            scroll = 0
        elif ch == ord('G'):
            scroll = max_scroll


# ── Editor ──────────────────────────────────────────────────────────────────

def journal_editor(stdscr, accent, prompt_text=None):
    """
    Write-once journal editor.
    Returns the entry text, or None if cancelled with nothing written.
    """
    lines = ['']
    cx, cy = 0, 0
    scroll_y = 0
    target_screen_cx = None

    # Calculate prompt display height for offset
    prompt_lines = []
    prompt_h = 0
    if prompt_text:
        import textwrap
        h, w = stdscr.getmaxyx()
        wrapped = textwrap.fill(prompt_text, width=w - 6)
        prompt_lines = wrapped.split('\n')
        prompt_h = len(prompt_lines) + 3  # blank line + prompt lines + blank line + separator

    curses.curs_set(1)

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        text_h = h - 2 - prompt_h  # status + help + prompt area

        # Clamp cursor
        cy = max(0, min(cy, len(lines) - 1))
        cx = max(0, min(cx, len(lines[cy])))

        # Build wrap map
        vrows = build_wrap_map(lines, w)
        vi_cursor, scx_cursor = logical_to_visual(vrows, cy, cx)

        # Scroll
        if vi_cursor < scroll_y:
            scroll_y = vi_cursor
        if vi_cursor >= scroll_y + text_h:
            scroll_y = vi_cursor - text_h + 1
        scroll_y = max(0, min(scroll_y, max(0, len(vrows) - text_h)))

        # Draw prompt area at top
        draw_row = 0
        if prompt_text:
            draw_row += 1  # blank line
            for pl in prompt_lines:
                try:
                    stdscr.addstr(draw_row, 3, pl, accent | curses.A_DIM)
                except curses.error:
                    pass
                draw_row += 1
            draw_row += 1  # blank line
            # Thin separator
            sep = "─" * (w - 2)
            try:
                stdscr.addstr(draw_row, 1, sep, curses.A_DIM)
            except curses.error:
                pass
            draw_row += 1

        # Draw text
        for i in range(text_h):
            vi = scroll_y + i
            if vi >= len(vrows):
                break
            li, scol, ecol = vrows[vi]
            segment = lines[li][scol:ecol]
            try:
                stdscr.addstr(draw_row + i, 0, segment)
            except curses.error:
                pass

        # Help bar
        draw_help_bar(stdscr, " ^W Terminer et sauvegarder  ^Q Abandonner")

        # Status bar
        wc = word_count(lines)
        _now = datetime.now()
        _mois = ["jan", "fév", "mar", "avr", "mai", "juin",
                 "juil", "août", "sep", "oct", "nov", "déc"]
        date_display = f"{_now.day:02d} {_mois[_now.month - 1]} {_now.year}"
        mode = "guidée" if prompt_text else "Écriture libre"
        left = f" {date_display}  ·  {mode}"
        right = f"lg {cy + 1}/{len(lines)}  {wc}m "
        draw_status(stdscr, left=left, right=right)

        # Cursor
        screen_row = draw_row + (vi_cursor - scroll_y)
        try:
            stdscr.move(screen_row, scx_cursor)
        except curses.error:
            pass

        stdscr.refresh()
        try:
            ch = stdscr.get_wch()
        except curses.error:
            continue
        continue_sticky = False

        # ── Navigation ──

        if ch == curses.KEY_UP:
            if vi_cursor > 0:
                if target_screen_cx is None:
                    target_screen_cx = scx_cursor
                cy, cx = visual_to_logical(vrows, vi_cursor - 1, target_screen_cx)
            continue_sticky = True

        elif ch == curses.KEY_DOWN:
            if vi_cursor < len(vrows) - 1:
                if target_screen_cx is None:
                    target_screen_cx = scx_cursor
                cy, cx = visual_to_logical(vrows, vi_cursor + 1, target_screen_cx)
            continue_sticky = True

        elif ch == curses.KEY_LEFT:
            if cx > 0:
                cx -= 1
            elif cy > 0:
                cy -= 1
                cx = len(lines[cy])

        elif ch == curses.KEY_RIGHT:
            if cx < len(lines[cy]):
                cx += 1
            elif cy < len(lines) - 1:
                cy += 1
                cx = 0

        elif ch == curses.KEY_HOME:
            li, scol, ecol = vrows[vi_cursor]
            cx = scol

        elif ch == curses.KEY_END:
            li, scol, ecol = vrows[vi_cursor]
            cx = ecol

        elif ch == curses.KEY_PPAGE:
            target_vi = max(0, vi_cursor - text_h)
            if target_screen_cx is None:
                target_screen_cx = scx_cursor
            cy, cx = visual_to_logical(vrows, target_vi, target_screen_cx)
            continue_sticky = True

        elif ch == curses.KEY_NPAGE:
            target_vi = min(len(vrows) - 1, vi_cursor + text_h)
            if target_screen_cx is None:
                target_screen_cx = scx_cursor
            cy, cx = visual_to_logical(vrows, target_vi, target_screen_cx)
            continue_sticky = True

        # ── Editing ──

        elif ch in (curses.KEY_BACKSPACE, '\x7f', '\x08'):
            if cx > 0:
                lines[cy] = lines[cy][:cx - 1] + lines[cy][cx:]
                cx -= 1
            elif cy > 0:
                cx = len(lines[cy - 1])
                lines[cy - 1] += lines[cy]
                lines.pop(cy)
                cy -= 1

        elif ch == curses.KEY_DC:
            if cx < len(lines[cy]):
                lines[cy] = lines[cy][:cx] + lines[cy][cx + 1:]
            elif cy < len(lines) - 1:
                lines[cy] += lines[cy + 1]
                lines.pop(cy + 1)

        elif ch in (curses.KEY_ENTER, '\n', '\r'):
            rest = lines[cy][cx:]
            lines[cy] = lines[cy][:cx]
            cy += 1
            lines.insert(cy, rest)
            cx = 0

        elif ch == '\t':  # Tab
            spaces = " " * TAB_WIDTH
            lines[cy] = lines[cy][:cx] + spaces + lines[cy][cx:]
            cx += TAB_WIDTH

        # ── Commands ──

        elif ch == '\x17':  # Ctrl+W — Terminer et sauvegarder
            text = '\n'.join(lines).strip()
            if not text:
                curses.curs_set(0)
                return None
            curses.curs_set(0)
            return text

        elif ch == '\x11':  # Ctrl+Q — Annuler
            text = '\n'.join(lines).strip()
            if text:
                if confirm(stdscr, "abandonner cette entrée ?"):
                    curses.curs_set(0)
                    return None
                curses.curs_set(1)
            else:
                curses.curs_set(0)
                return None

        elif ch == '\x1b':  # Esc — same as Ctrl+Q
            text = '\n'.join(lines).strip()
            if text:
                if confirm(stdscr, "abandonner cette entrée ?"):
                    curses.curs_set(0)
                    return None
                curses.curs_set(1)
            else:
                curses.curs_set(0)
                return None

        # ── Printable ──

        elif isinstance(ch, str) and ch >= ' ':
            lines[cy] = lines[cy][:cx] + ch + lines[cy][cx:]
            cx += 1

        if not continue_sticky:
            target_screen_cx = None

# ── Main ────────────────────────────────────────────────────────────────────

def main(stdscr):
    locale.setlocale(locale.LC_ALL, '')
    curses.start_color()
    curses.raw()
    stdscr.keypad(True)
    curses.use_default_colors()
    curses.set_escdelay(25)
    curses.curs_set(0)

    # Colors
    curses.init_pair(1, curses.COLOR_YELLOW, -1)
    accent = curses.color_pair(1)

    ensure_journal_dir()

    while True:
        action = draw_main_screen(stdscr, accent)

        if action is None:
            break

        if action == "view":
            # Browse and view past entries
            while True:
                filename = entry_browser(stdscr, accent)
                if filename is None:
                    break
                entry_viewer(stdscr, accent, filename)
            continue

        # Select prompt
        if action == "prompt":
            prompt_text = random.choice(PROMPTS)
        else:
            prompt_text = None

        # Write entry
        text = journal_editor(stdscr, accent, prompt_text=prompt_text)

        if text is None:
            continue

        # Prepend prompt to saved text if applicable
        if prompt_text:
            full_text = f"PROMPT: {prompt_text}\n\n{text}"
        else:
            full_text = f"FREEWRITE\n\n{text}"

        # Add metadata
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        wc = len(text.split())
        header = f"DATE: {timestamp}\nWORDS: {wc}\n\n"
        full_text = header + full_text

        save_entry(full_text)


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    print("au revoir.")