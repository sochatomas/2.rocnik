# Zadanie 4 dokumentácia
## Matej Skyčák, Tomáš Socha

## Popis riešenia
### 1. Registrácia
Každý novovytvorený používateľ z tabuľky "pouzivatelia" musí byť registrovaný, teda sa pre neho vytvorí záznam v tabuľke "registracia". Tu sa podľa toho, akým spôsobom sa registroval uložia potrebné informácie. Ak sa registroval pomocou nejakej služby tretích strán, tak sa použije ID používateľa v danej službe (Google,Facebook,...). Spôsoby registrá sú uložené v tabuľke "sluzby_na_registrovanie". Ak sa chce registrovať pomocou e-mailu, tak zadá meno, heslo a mail, kde mu taktiež príde mail na overenie registrácie.

### 2. Priateľstva
Jednotlivé postavy vedia byť navzájom priatelia, záznamy (páry) priateľov uchovávame v tabuľke "priatelstva". Pre každú postavu si taktiež uchovávame ich level a iné informácie, takže je možné sledovať progres medzi priateľmi. Tabuľka "pozvanky" slúži na ukladanie pozvánok a obsahuje informácie o tom, kto komu poslal pozvánku, či bola prijatá alebo zamietnutá a či už na ňu prijímateľ reagoval. 

### 3. Tímy
Postavy vedia byť taktiež v tímoch (každá maximálne v jednom), ktorý je presne špecifikovaný jedinečným menom. Rovnako ako pozvánka do tímu obsahuje s ňou súvisiace informácie. Jediný rozdiel je v tom, že sa pri tímovej pozvánke úloží aj informácia, že ide o tímovú a nie priateľskú pozvánku a na základe tímu odosielateľa sa rozhodne do akého tímu je prijímateľ pozvaný.

### 4. Chat
Každé priateľstvo aj tím, musia mať k ním prisluchajúci chat, informácie o jednotlivých chatoch sú uchované v tabuľke "chat". Každý chat sa skladá zo správ, a záznamy o jednotlivých správach sa uchovávajú v tabuľke "spravy", kde sú taktiež informácie o tom, kto a kedy správu napísal, ktorému chatu prislúchajú a ich obsah. 

### 5. Postava
Jednotlivé záznamy o postavách, ktoré si používatelia vytvorili sa nachádzajú v tabuľke "instancie_postav". Používateľ si pri vytváraní postavy vie vybrať z rôznych rolí, tie sú v tabuľke "role". Každá postava môže, ale nemusí mať priradený tím. Ak tím má, tak v atribúte "tim_status" je informácie jej postavení v tíme (či vie pozývať členov, či vie rozpustiť tím,...). Každá postava má meno, ktoré je jedinečné. Záznam o postave obsahuje aj informáciu o jej leveli, o jej aktuálnom počte experience bodov a rovnako tak aj koľko jej chýba do ďalšieho levelu. V atribúte "je_online" je informácia, či je používateľ aktuálne prihlásený za danú postavu. Postave je taktiež priradená konkrétna inštancia mapy, na ktorej je presne určená pomocou atribútov "x_pozicia" a "y_pozicia". Aby mal používateľ možnost jednotlivé postavy mazať, meniť ich mená a vedieť, kedy boli vytvorené, sú pre každú postavu vedené atribúty "datum_vytvorenia", "datum_zmeny" a "datum_vymazania".

### 6. Príšery
Záznamy o jednotlivých druhoch prišer sú v tabuľke "prisery". Obdobne ako aj postavy majú svoje základné parametre reprezentovné atribútmi: názov, max_zdravie, utok a obrana. Záznamy majú atribúty min_level a max_level, aby sa dalo určiť,ktorým postavám sa majú zobrazovať. Každý záznam obsahuje informáciu o tom, ktorý predmet z nej môže padnúť a koľko experience bodov je možné za jej zabitie získať. Taktiež aby bolo možné určiť, krorá ďalšia príšery sa má narodiť majú záznamy odkaz na rodičovskú príšeru (id_rodicovskej_prisery) Už konkrétne inštancie príšer sú v tabuľke "instancie_priser" a majú priradené, o aký typ príšery sa jedná a koľko má aktuálne zdravia. Ďalej majú priradenú konkrétnu inštanciu mapy, kde sa nachádza a taktieť príslušné súradnice "x_pozicia" a "y_pozicia".

### 7. Úlohy
Záznamy o jednotlivých typoch úloh sú uložené v tabuľke "ulohy", kde každému typu je priradená uroveň mapy, na ktorej sa dá splniť, potrebný level a nejaká príšera, ktorú treba zabiť a koľkokrát. Aby bolo možné sledovať progres hráča v jednotlivých úlohach (mnozstvo_zabitych) a či ich už splnil sú vedené záznamy v tabulke "postavy_ulohy".

### 8. Schopnosti
Jednotlivé druhy schopností sú v tabuľke "schopnosti", tam je špecifikovaný ich názov a doba, za akú je možné ich opätovne použiť. Aby mohli mať schopnosti stromovú hierarchiu je potrebne si v tabulke "prerekvizity" ukladať jednotlivé páry schopností spolu so schopnosťou, ktorú je potrebné mať vybratú. Záznamy o schopnostiach, ktoré má konkrétna postava vybraté sa nachádzajú v tabuľke "postavy_schopnosti". 

### 9. Roly
V tabuľke "roly" sa nachádza informácia pre každú rolu, o koľko sa zvýšia jej základné parametre za dosiahnutie nového levelu. Tie sa prirátajú v tabulke "instancie_postav" k jednotlivým parametrom(max_zdravie, utok, obrana), podľa toho akú rolu má daná postava vybratú.

### 10. Mapa
Mapa je rozdelená na jednotlivé úrovne, o ktorých záznamy sú v tabuľke "urovne_mapy". Tu pre každú úroveň mapy uchovávame informáciu o tom aká je veľká, reprezentácia obdĺžnikom (prípadne štvorcom). Bod úplne vľavo dole má súradnice (0,0) a bod úplne vpravo hore má súradnice (max_x, max_y), ktoré sú dané pre každú úroveň. Taktiež každá úroveň je prístupná od určitého levelu (min_level).

### 11. Predmety
Záznamy o tom, aké predmety je možné v hre nájsť sa nachádzajú v tabuľke predmety, záznamy obsahujú atribúty ako názov predmetu, potrebný level na jeho vybavenie a koľko bodov pridáva k základnym parametrom postave, ktorá ho má vybavený. To aké má postava vybavené predmety je uložené v tabuľke "postavy_predmety". Aby bola splnená podmienka, že predmety je možné nájsť aj na rôznych urovniach mapy a taktiež, či už boli zobraté, je potrebné viesť záznamy o konkrétnych predmetoch na konkrétnej úrovni mapy (tabuľka instancie_predmetov). Jednotlivé inštancie predmetov obsahujú atribúty (x_pozicia, y_pozicia), ktoré reprezentujú to, kde presne sa predmet nachádza.

### 12. Záznamy bojov
Jednotlivé záznamy bojov sú uložené v tabuľke "zaznam_bojov", tu je pre každý záznam ukladané, kde, kedy a medzi kým boj nastal a taktiež koľko zdravia zúčastneným po skončení ostalo. Jednotlivé udalosti v rámci jedného boja sú uložené v tabuľke "pouzite_schopnosti", kde na základe prepojenia s tabuľkou "postavy_schopnosti" vieme určiť, kto použil akú schopnosť.

## Popis hry
Inšpirovali sme sa MMORPG hrou Metin2, z ktorej sme prevzali viaceré mechanizmy. Napríklad to, že postava má jeden tím (niečo ako cech) a má zoznam priateľov, kde vidí, či sú online, prípadne im vie napísať správu. Na to aby mohol hrať používateľ v nejakej hre je potrebné, aby sa najprv registroval. Po registrácii si vytvorí postavu (prípadne aj ďalšie postavy) a spolu s postavami iných používateľov vie vytvoriť hru. 

Nad hrou ako takou, sme rozmýšľali ako prepojenie medzi inštanciami úrovni máp, spolu s postavami a predmetmi, ktoré im patria. Teda keď sa vytvorí jedna hra, vytvorí sa pre ňu 20 záznamov úrovní, z ktotých vieme vytvoriť konkrétnu hru. Medzi úrovňami podobne ako v Metin2 sa vie postava presúvať pomocou portálu, až kým dôjde na nejakú finálnu úroveň, z ktorej sa už ďalej dostať nevie (vie ísť jedine späť). Každá úroveň má priradenú nejakú sadu úloh, ktoré je možné splniť len na tej konkrétnej úrovni v ľubovoľnom poradí. Na jednotlivých úrovniach sa nachádzajú na konkrétnych miestach predmety a príšery. Pre vstup na konkrétnu úroveň mapy, rovnako tak aj pre plnenie konkrétnej úlohy musí mať postava potrebný level. 

Za prejdenie hry považujeme, splnenie poslednej úlohy (zabitie bossa), čo však neznamená koniec hry, hráč môže hrať ďalej a plniť úlohy, ktoré ešte nesplnil. Taktiež hráč nemusí plniť úlohy a môže len tak voľne behať, takže je to "open-world" hra.
