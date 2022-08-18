# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 20:50:21 2022

Script that daily update temperature and pressure datasets - cronjob every day at 7am

@author: Edwin Cifuentes - Team30 DS4A - Cohort 6
Finish date: 7 de julio de 2022
"""

#!pip install sodapy
import pandas as pd
import numpy as np
import time
from datetime import datetime
from datetime import timedelta
from sodapy import Socrata

def optain_divipola(dep,mun,divipola):
    dep = str(dep).strip()
    mun = str(mun).strip()
    parentesis = str(mun).find("(")
    if parentesis > -1:
        mun = mun[:parentesis].strip()
    consulta = divipola[(divipola["Nombre Departamento"] == dep) & (divipola["Nombre Municipio"]==mun)]["Código Municipio"]
    resultado = str(consulta.min()) if len(consulta)>0 else np.nan
    return resultado

dic_mun = {"EL ATRATO":"EL CARMEN DE ATRATO",
           "CÚCUTA":"SAN JOSÉ DE CÚCUTA",
           "CARTAGENA":"CARTAGENA DE INDIAS",
           "BOGOTA D.C.":"BOGOTÁ. D.C.",
           "BOGOTA, D.C":"BOGOTÁ. D.C.",
           "BOGOTA, D.C.":"BOGOTÁ. D.C.",
           "EL TABLÓN":"EL TABLÓN DE GÓMEZ",
           "TUMACO":"SAN ANDRÉS DE TUMACO",
           "VILLAMARIA":"VILLAMARÍA",
           "JURADO":"JURADÓ",
           "EL CARMÉN DE BOLÍVAR":"EL CARMEN DE BOLÍVAR",
           "PISVA":"PISBA",
           "VILLA DE LEIVA":"VILLA DE LEYVA",
           "GUICÁN":"GÜICÁN DE LA SIERRA",
           "PIVIJAI":"PIVIJAY",
           "SAN ANDRES Y PROVIDENCIA (SANTA ISABEL)":"PROVIDENCIA",
           "SAN ANDRES Y  PROVIDENCIA (SANTA ISABEL)":"PROVIDENCIA",
           "ENTRERRIOS":"ENTRERRÍOS",
           "BUGA":"GUADALAJARA DE BUGA",
           "TOLÚ":"SANTIAGO DE TOLÚ",
           "CHINCHINA":"CHINCHINÁ",
           "SUPIA":"SUPÍA",
           "ZETAQUIRÁ":"ZETAQUIRA",
           "UBATÉ":"VILLA DE SAN DIEGO DE UBATÉ",
           "BELALCAZAR":"BELALCÁZAR",
           "SAN JOSE":"SAN JOSÉ",
           "SANTA FE DE ANTIOQUIA":"SANTA FÉ DE ANTIOQUIA",
           "PIENDAMÓ":"PIENDAMÓ - TUNÍA",
           "EL PAUJIL":"EL PAUJÍL",
           "RIO QUITO (PAIMADÓ)":"RÍO QUITO",
           "RIO IRO":"RÍO IRÓ",
           "LITORAL DEL SAN JUAN":"EL LITORAL DEL SAN JUAN",
           "MARIQUITA":"SAN SEBASTIÁN DE MARIQUITA",
           "VIGIA DEL FUERTE":"VIGÍA DEL FUERTE",
           "MANI":"MANÍ",
           "IBAGUE":"IBAGUÉ",
           "MEDELLIN":"MEDELLÍN",
           "QUIBDO":"QUIBDÓ",
           "PLANETARICA":"PLANETA RICA",
           "PUERTO LIBERTADOr":"PUERTO LIBERTADOR",
           "PUERTO LOPEZ":"PUERTO LÓPEZ",
           "POPAYAN":"POPAYÁN",
           "JAMUNDI":"JAMUNDÍ",
           "CARMEN DE APICALA":"CARMEN DE APICALÁ",
           "CAPARRAPI":"CAPARRAPÍ",
           "PEÑON":"EL PEÑÓN",
           " EL CALVARIO":"EL CALVARIO",
           "PUERTO GAITAN":"PUERTO GAITÁN",
           "CAQUEZA":"CÁQUEZA",
           "CUCUTA":"SAN JOSÉ DE CÚCUTA",
           "CIENAGA":"CIÉNAGA",
           "LIBANO":"LÍBANO",
           "FUSAGASUGA":"FUSAGASUGÁ",
           "CALARCA":"CALARCÁ",
           "GIRON":"GIRÓN",
           "BOGOTA":"BOGOTÁ. D.C.",
           "OROCUE":"OROCUÉ",
           "FOMEQUE":"FÓMEQUE",
           "MONTERIA":"MONTERÍA",
           "GARZON":"GARZÓN",
           "SUAREZ":"SUÁREZ",
           "PUERTO BOYACA":"PUERTO BOYACÁ",
           "CAJIBIO":"CAJIBÍO",
           "MISTRATO":"MISTRATÓ",
           "APIA":"APÍA",
           "PURIFICACION":"PURIFICACIÓN",
           "JUNIN":"JUNÍN",
           "GACHETA":"GACHETÁ",
           "GUATICA":"GUÁTICA",
           "VIOTA":"VIOTÁ",
           "BELEN DE UMBRIA":"BELÉN DE UMBRÍA",
           "TIMBIO":"TIMBÍO",
           "TIMANA":"TIMANÁ",
           "UTICA":"ÚTICA",
           "TIMBIQUI":"TIMBIQUÍ",
           "SAN JOSE DEL GUAVIARE":"SAN JOSÉ DEL GUAVIARE",
           "INIRIDA":"INÍRIDA",
           "CHOACHI":"CHOACHÍ",
           "QUINCHIA":"QUINCHÍA",
           "SAN VICENTE DE CHUCURI":"SAN VICENTE DE CHUCURÍ",
           "GUACHETA":"GUACHETÁ",
           "ZIPAQUIRA":"ZIPAQUIRÁ",
           "YAGUARA":"YAGUARÁ",
           "ABREGO":"ABREGÓ",
            "PATIA":"PATÍA",
            "NUNCHIA":"NUNCHÍA",
            "NACION":"NACIÓN",
            "SIBATE":"SIBATÉ",
            "UBATE":"VILLA DE SAN DIEGO DE UBATÉ",
            "BOLIVAR":"BOLÍVAR",
            "FUNDACION":"FUNDACIÓN",
            "INZA":"INZÁ",
            "TIBU":"TIBÚ",
            "LLORO":"LLORÓ",
            "YACOPI":"YACOPÍ",
            "PUERTO ASIS":"PUERTO ASÍS",
            "TADO":"TADÓ",
            "LERIDA":"LÉRIDA",
            "ITAGUI":"ITAGÜÍ",
            "EL PLAYON":"EL PLAYÓN",
            "MEDIO BAUDO":"MEDIO BAUDÓ",
            "PUERTO LEGUIZAMO":"PUERTO LEGUÍZAMO",
            "SAMACA":"SAMACÁ",
            "APARTADO":"APARTADÓ",
            "SAN MARTIN":"SAN MARTÍN",
            "MITU":"MITÚ",
            "UBALA":"UBALÁ",
            "LOPEZ DE MICAY":"LÓPEZ DE MICAY",
            "SAN ANDRES DE TUMACO":"SAN ANDRÉS DE TUMACO",
            "MONTELIBANO":"MONTELÍBANO",
            "GENOVA":"GÉNOVA",
            "ACACIAS":"ACACÍAS",
           "ABREGÓ":"ÁBREGÓ",
           "ÁBREGÓ":"ÁBREGO",
            "SAN ANDRES":"SAN ANDRÉS",
            "GALAN":"GALÁN",
            "SAN VICENTE DEL CAGUAN":"SAN VICENTE DEL CAGUÁN",
            "FACATATIVA":"FACATATIVÁ",
            "CURUMANI":"CURUMANÍ",
            "CHIGORODO":"CHIGORODÓ",
            "NATAGA":"NÁTAGA",
            "PAEZ":"PÁEZ",
            "BAJO BAUDO":"BAJO BAUDÓ",
            "PUERTO GUZMAN":"PUERTO GUZMÁN",
            "CHITAGA":"CHITAGÁ",
            "SAN AGUSTIN":"SAN AGUSTÍN",
            "CHACHAGUI":"CHACHAGÜÍ",
            "ALTO BAUDO":"ALTO BAUDÓ",
            "GUTIERREZ":"GUTIÉRREZ",
            "BOJAYA":"BOJAYÁ",
            "DEPARTAMENTO":"DEPARTAMENTO",
            "NECHI":"NECHÍ",
            "SANTA MARIA":"SANTA MARÍA",
            "CHOCONTA":"CHOCONTÁ",
            "MAGANGUE":"MAGANGUÉ",
            "CUCUNUBA":"CUCUNUBÁ",
            "AMAGA":"AMAGÁ",
            "MANATI":"MANATÍ",
            "BAHIA SOLANO":"BAHÍA SOLANO",
            "RAQUIRA":"RÁQUIRA",
            "GACHALA":"GACHALÁ",
            "VELEZ":"VÉLEZ",
            "PUERTO BERRIO":"PUERTO BERRÍO",
            "LA UNION":"LA UNIÓN",
            "UNGUIA":"UNGUÍA",
            "AGUSTIN CODAZZI":"AGUSTÍN CODAZZI",
            "SANDONA":"SANDONÁ",
            "SOTARA":"SOTARÁ",
            "CHINACOTA":"CHINÁCOTA",
            "COCORNA":"COCORNÁ",
            "CHIA":"CHÍA",
            "CARMEN DEL DARIEN":"CARMEN DEL DARIÉN",
            "TAMARA":"TÁMARA",
            "ALBAN":"ALBÁN",
            "BOJACA":"BOJACÁ",
            "IQUIRA":"ÍQUIRA",
            "MONIQUIRA":"MONIQUIRÁ",
            "CORDOBA":"CÓRDOBA",
            "NOVITA":"NÓVITA",
            "TOPAIPI":"TOPAIPÍ",
            "TORIBIO":"TORIBÍO",
            "PURACE":"PURACÉ",
            "SAMANA":"SAMANÁ",
            "CONSACA":"CONSACÁ",
            "VILLAGARZON":"VILLAGARZÓN",
            "TOCANCIPA":"TOCANCIPÁ",
            "TUQUERRES":"TÚQUERRES",
            "ACHI":"ACHÍ",
           "SOTARÁ":"SOTARÁ PAISPAMBA",
            "ROBERTO PAYAN":"ROBERTO PAYÁN",
            "CHIQUINQUIRA":"CHIQUINQUIRÁ",
            "RIO QUITO":"RÍO QUITO",
            "PIENDAMO":"PIENDAMÓ",
            "VILLAPINZON":"VILLAPINZÓN",
            "ANZOATEGUI":"ANZOÁTEGUI",
            "CACHIRA":"CÁCHIRA",
            "BAGADO":"BAGADÓ",
            "SAN JUAN DE RIO SECO":"SAN JUAN DE RIOSECO",
            "FUQUENE":"FÚQUENE",
            "MALAGA":"MÁLAGA",
            "ANORI":"ANORÍ",
            "CURITI":"CURITÍ",
            "CERETE":"CERETÉ",
            "NECOCLI":"NECOCLÍ",
            "REPELON":"REPELÓN",
            "TARAZA":"TARAZÁ",
            "BELTRAN":"BELTRÁN",
            "CIENAGA DE ORO":"CIÉNAGA DE ORO",
            "CARTAGENA DEL CHAIRA":"CARTAGENA DEL CHAIRÁ",
            "QUIPAMA":"QUÍPAMA",
            "SANTA BARBARA":"SANTA BÁRBARA",
           "PIENDAMÓ":"PIENDAMÓ - TUNÍA",
            "VILLAGOMEZ":"VILLAGÓMEZ",
            "TIBANA":"TIBANÁ",
            "NEMOCON":"NEMOCÓN",
            "LEJANIAS":"LEJANÍAS",
            "CHIRIGUANA":"CHIRIGUANÁ",
            "MAGUI PAYAN":"MAGÜÍ",
            "SESQUILE":"SESQUILÉ",
            "SOATA":"SOATÁ",
            "SOCOTA":"SOCOTÁ",
            "YONDO":"YONDÓ",
            "SIMITI":"SIMITÍ",
            "CAJICA":"CAJICÁ",
            "LOS CORDOBAS":"LOS CÓRDOBAS",
            "BELEN":"BELÉN",
            "ACANDI":"ACANDÍ",
            "EL PEÑON":"EL PEÑÓN",
            "TULUA":"TULUÁ",
            "LANDAZURI":"LANDÁZURI",
            "GAMEZA":"GÁMEZA",
            "SANTIAGO DE TOLU":"SANTIAGO DE TOLÚ",
            "SOTAQUIRA":"SOTAQUIRÁ",
            "EL CARMEN DE BOLIVAR":"EL CARMEN DE BOLÍVAR",
           "RIOFRIO":"RIOFRÍO",
            "EL AGUILA":"EL ÁGUILA",
            "GUACARI":"GUACARÍ",
            "ARBELAEZ":"ARBELÁEZ",
            "CACOTA":"CÁCOTA",
            "TOTORO":"TOTORÓ",
            "EL TABLON DE GOMEZ":"EL TABLÓN DE GÓMEZ",
            "GUAYABAL DE SIQUIMA":"GUAYABAL DE SÍQUIMA",
            "MURINDO":"MURINDÓ",
            "VIANI":"VIANÍ",
            "CUBARA":"CUBARÁ",
            "SAN JOSE DEL PALMAR":"SAN JOSÉ DEL PALMAR",
            "SAN SEBASTIAN":"SAN SEBASTIÁN",
            "BELEN DE LOS ANDAQUIES":"BELÉN DE LOS ANDAQUÍES",
            "COLON":"COLÓN",
            "SIPI":"SIPÍ",
            "SAN VICENTE":"SAN VICENTE FERRER",
            "MUTATA":"MUTATÁ",
            "GAMBITA":"GÁMBITA",
            "VEGACHI":"VEGACHÍ",
            "ANDALUCIA":"ANDALUCÍA",
           "BARRANCA DE UPIA":"BARRANCA DE UPÍA",
            "CACERES":"CÁCERES",
            "CEPITA":"CEPITÁ",
            "CANTON DE SAN PABLO":"EL CANTÓN DEL SAN PABLO",
            "CHARALA":"CHARALÁ",
            "MAPIRIPAN":"MAPIRIPÁN",
            "SAN JOSE DEL FRAGUA":"SAN JOSÉ DEL FRAGUA",
            "SAMPUES":"SAMPUÉS",
            "PUERTO RONDON":"PUERTO RONDÓN",
            "JERICO":"JERICÓ",
            "PARAMO":"PÁRAMO",
            "CERTEGUI":"CÉRTEGUI",
            "NUQUI":"NUQUÍ",
            "SANTO TOMAS":"SANTO TOMÁS",
            "MACHETA":"MACHETÁ",
            "COMBITA":"CÓMBITA",
            "RAMIRIQUI":"RAMIRIQUÍ",
            "ANGELOPOLIS":"ANGELÓPOLIS",
            "SAHAGUN":"SAHAGÚN",
            "BOYACA":"BOYACÁ",
            "ARIGUANI":"ARIGUANÍ",
            "SURATA":"SURATÁ",
            "PAZ DE RIO":"PAZ DE RÍO",
            "CONVENCION":"CONVENCIÓN",
            "HACARI":"HACARÍ",
            "PULI":"PULÍ",
            "SAN JERONIMO":"SAN JERÓNIMO",
            "SONSON":"SONSÓN",
            "SAN MARTIN DE LOBA":"SAN MARTÍN DE LOBA",
            "RIO VIEJO":"RÍO VIEJO",
            "SANTAFE DE ANTIOQUIA":"SANTA FÉ DE ANTIOQUIA",
            "SANTA LUCIA":"SANTA LUCÍA",
            "CHIQUIZA":"CHÍQUIZA",
            "SAN JOSE DE MIRANDA":"SAN JOSÉ DE MIRANDA",
            "TAMESIS":"TÁMESIS",
            "RIO DE ORO":"RÍO DE ORO",
            "ALCALA":"ALCALÁ",
            "MARIPI":"MARIPÍ",
            "HERRAN":"HERRÁN",
            "CARCASI":"CARCASÍ",
            "PACORA":"PÁCORA",
            "CARACOLI":"CARACOLÍ",
            "ANZA":"ANZÁ",
            "ZIPACON":"ZIPACÓN",
            "TOLU VIEJO":"TOLÚ VIEJO",
            "CUITIVA":"CUÍTIVA",
            "TURMEQUE":"TURMEQUÉ",
            "SOPO":"SOPÓ",
            "TUBARA":"TUBARÁ",
            "CONCEPCION":"CONCEPCIÓN",
            #"RIO IRÓ":"RÍO IRÓ",
            "TOPAGA":"TÓPAGA",
           "TOLÚ VIEJO":"SAN JOSÉ DE TOLUVIEJO",
            "JAMBALO":"JAMBALÓ",
            "TINJACA":"TINJACÁ",
            "GACHANCIPA":"GACHANCIPÁ",
            "EL CONTADERO":"CONTADERO",
            "SABOYA":"SABOYÁ",
            "YOLOMBO":"YOLOMBÓ",
            "NOROSI":"NOROSÍ",
            "SORACA":"SORACÁ",
            "POTOSI":"POTOSÍ",
            "CIUDAD BOLIVAR":"CIUDAD BOLÍVAR",
            "ELIAS":"ELÍAS",
            "EL PIÑON":"EL PIÑÓN",
            "EL RETEN":"EL RETÉN",
            "GUACHENE":"GUACHENÉ",
            "EBEJICO":"EBÉJICO",
            "SACHICA":"SÁCHICA",
            "GUICAN":"GÜICÁN DE LA SIERRA",
            "SUPATA":"SUPATÁ",
            "UNION PANAMERICANA":"UNIÓN PANAMERICANA",
            "BURITICA":"BURITICÁ",
            "MARIA LA BAJA":"MARÍA LA BAJA",
            "TITIRIBI":"TITIRIBÍ",
            "CIENEGA":"CIÉNEGA",
            "VALPARAISO":"VALPARAÍSO",
            "CHIVATA":"CHIVATÁ",
            "SAN CRISTOBAL":"SAN CRISTÓBAL",
            "SANTA ROSALIA":"SANTA ROSALÍA",
            "SAN LUIS DE SINCE":"SAN LUIS DE SINCÉ",
            "VALLE DE SAN JOSE":"VALLE DE SAN JOSÉ",
            "CONTRATACION":"CONTRATACIÓN",
            "GUAVATA":"GUAVATÁ",
            "SANTA HELENA DEL OPON":"SANTA HELENA DEL OPÓN",
            "SAN JOAQUIN":"SAN JOAQUÍN",
            "IMUES":"IMUÉS",
            "LA URIBE":"URIBE",
            "SANTA BARBARA DE PINTO":"SANTA BÁRBARA DE PINTO",
            "ZAPAYAN":"ZAPAYÁN",
            "DISTRACCION":"DISTRACCIÓN",
            "CHAGUANI":"CHAGUANÍ",
            "BOGOTA":"BOGOTÁ. D.C.",
            "PURISIMA":"PURÍSIMA DE LA CONCEPCIÓN",
            "SAN JOSE DE URE":"SAN JOSÉ DE URÉ",
            "CHINU":"CHINÚ",
            "CHAMEZA":"CHÁMEZA",
            "MILAN":"MILÁN",
            "SUTAMARCHAN":"SUTAMARCHÁN",
            "MONGUI":"MONGUÍ",
            "NUEVO COLON":"NUEVO COLÓN",
            "PIOJO":"PIOJÓ",
            "USIACURI":"USIACURÍ",
            "DON MATIAS":"DONMATÍAS",
            "YALI":"YALÍ",
            "GOMEZ PLATA":"GÓMEZ PLATA",
            "JERUSALEN":"JERUSALÉN",
            "SUSACON":"SUSACÓN",
            "GUATAPE":"GUATAPÉ",
            "JARDIN":"JARDÍN",
            "SAN ANDRES DE CUERQUIA":"SAN ANDRÉS DE CUERQUÍA",
            "SAN JUAN DE URABA":"SAN JUAN DE URABÁ",
            #"SAN PEDRO":"SAN PEDRO DE LOS MILAGROS",
            "SAN PEDRO DE URABA":"SAN PEDRO DE URABÁ",
            "SOPETRAN":"SOPETRÁN",
            "CARMEN DE BOLIVAR":"EL CARMEN DE BOLÍVAR",
            "MOMPOS":"SANTA CRUZ DE MOMPOX",
            "MOMPOX":"SANTA CRUZ DE MOMPOX",
            "TURBANA":"TURBANÁ",
            "COVARACHIA":"COVARACHÍA",
            "GUAYATA":"GUAYATÁ",
            "OICATA":"OICATÁ",
            "SAN JOSE DE PARE":"SAN JOSÉ DE PARE",
            "SANTA SOFIA":"SANTA SOFÍA",
            "TOGUI":"TOGÜÍ",
            "VIRACACHA":"VIRACACHÁ",
            "SACAMA":"SÁCAMA",
            "GONZALEZ":"GONZÁLEZ",
            "BOGOTA":"BOGOTÁ. D.C.",
            "GUATAQUI":"GUATAQUÍ",
            "CHIBOLO":"CHIVOLO",
            "PUEBLO VIEJO":"PUEBLOVIEJO",
            "SAN SEBASTIAN DE BUENAVISTA":"SAN SEBASTIÁN DE BUENAVISTA",
            "SAN ZENON":"SAN ZENÓN",
            "CUASPUD":"CUASPUD CARLOSAMA",
            "GUALMATAN":"GUALMATÁN",
            "COLOSO":"COLOSÓ",
           "ALEJANDRIA":"ALEJANDRÍA",
            "MARIALABAJA":"MARÍA LA BAJA",
            "RIOVIEJO":"RÍO VIEJO",
            "GACHANTIVA":"GACHANTIVÁ",
            "RONDON":"RONDÓN",
            "UMBITA":"ÚMBITA",
            "CARMEN DE ATRATO":"EL CARMEN DE ATRATO",
            "CERRO SAN ANTONIO":"CERRO DE SAN ANTONIO",
            "SABANAS DE SAN ANGEL":"SABANAS DE SAN ÁNGEL",
            "LOS ANDES SOTOMAYOR":"LOS ANDES",
            "TABLON DE GOMEZ":"EL TABLÓN DE GÓMEZ",
            "SALAZAR DE LAS PALMAS":"SALAZAR",
            "VILLACARO":"VILLA CARO",
            "CHIPATA":"CHIPATÁ",
            "FLORIAN":"FLORIÁN",
            "GUAPOTA":"GUAPOTÁ",
            "GUEPSA":"GÜEPSA",
            "JESUS MARIA":"JESÚS MARÍA",
            "CHALAN":"CHALÁN",
            "SAN PEDRO DE LOS MILAGROS":"SAN PEDRO",
            "SINCE":"SAN LUIS DE SINCÉ",
            "TOLU":"SANTIAGO DE TOLÚ",
            "ARMERO GUAYABAL":"ARMERO",
            "HERBEO":"HERVEO",
            "RIO IRÓ":"RÍO IRÓ"

             }
dic_dep = {"CHOCO":"CHOCÓ",

           "SAN ANDRÉS PROVIDENCIA":"ARCHIPIÉLAGO DE SAN ANDRÉS. PROVIDENCIA Y SANTA CATALINA",
           "ARCHIPIELAGO DE SAN ANDRES, PROVIDENCIA Y SANTA CATALINA":"ARCHIPIÉLAGO DE SAN ANDRÉS. PROVIDENCIA Y SANTA CATALINA",
           "SAN ANDRES":"ARCHIPIÉLAGO DE SAN ANDRÉS. PROVIDENCIA Y SANTA CATALINA",
           "BOGOTA D.C.":"BOGOTÁ. D.C.",
           "BOGOTA ":"BOGOTÁ. D.C.",
           "BOGOTA":"BOGOTÁ. D.C.",
           "BOGOTA, D.C.":"BOGOTÁ. D.C.",
           "CORDOBA":"CÓRDOBA",
           "BOLIVAR":"BOLÍVAR",
           "ATLANTICO":"ATLÁNTICO",
           "CAQUETA":"CAQUETÁ",
           "NARINO":"NARIÑO",
           "QUINDIO":"QUINDÍO",
           "BOYACA":"BOYACÁ",
           "GUAINIA":"GUAINÍA",
           "VAUPES":"VAUPÉS",
           "VALLE":"VALLE DEL CAUCA",
           "VALLE ":"VALLE DEL CAUCA",
           "GUAJIRA":"LA GUAJIRA",
           "CESÁR":"CESAR"
    
}
divipola = pd.read_csv("datasets/DIVIPOLA.csv", dtype ={'Código Municipio':str}, encoding="utf-8")
divipola = divipola.dropna(subset=["Código Municipio"])

# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:
#client = Socrata("www.datos.gov.co", None)

# Example authenticated client (needed for non-public datasets):
client = Socrata('www.datos.gov.co',
                  'e57OPBK09DdELuozn9qlCSBtL',
                  username="edwin@cifuentes.com.co",
                  password="tozxeV-gokfon-1tixqo")

# First 2000 results, returned as JSON from API / converted to Python list of
# dictionaries by sodapy.
datasets = {
    #"precipitation":"s54a-sgyg",
    "pressure":"62tk-nxj5",
    "temperature":"sbwg-7ju4"
    }
new_data = {}

now_date_time = datetime.now()
yesterday = now_date_time - timedelta(days=1)
yesterday_str = yesterday.strftime("%Y-%m-%d")

for dataset in datasets:
    #print (datasets[dataset])
    result = client.get(datasets[dataset], select="*", where="fechaobservacion >= '"+yesterday_str+"T00:00:00.000'", limit=2000000)
    if len(result) > 0:    
        # Convert to pandas DataFrame
        df = pd.DataFrame.from_records(result)
        df.fechaobservacion = pd.to_datetime(df.fechaobservacion)
        df.valorobservado = df.valorobservado.astype(float)
        new_data[dataset]=df.groupby([df["fechaobservacion"].dt.date,df["codigoestacion"]]).agg(
                codigo_sensor=('codigosensor', min),
                nombre_estacion=('nombreestacion', min),
                departamento=('departamento', min),
                municipio=('municipio', min),
                zona_hidrografica=('zonahidrografica', min),
                latitud=('latitud', min),
                longitud=('longitud', min),
                unidad_medida=('unidadmedida', min),
                descripcion=('descripcionsensor', min),
                anio_observacion=("fechaobservacion",  lambda x: min(x).year),
                doy_observacion=("fechaobservacion",  lambda x: min(x).day_of_year),
                mes_observacion=("fechaobservacion",  lambda x: min(x).month),
                day_observacion=("fechaobservacion",  lambda x: min(x).day),
                valor_observado_avg=('valorobservado', 'mean'),
                valor_observado_min=('valorobservado', min),
                valor_observado_max=('valorobservado', max),
                valor_observado_std=('valorobservado', 'std'), 
                #valor_observado_suma=('valorobservado', sum), 
                #valor_observado_median=('valorobservado', 'median'),
                #observaciones=('valorobservado', 'count'),
                # Apply a lambda to date column
                # num_days=("date", lambda x: (max(x) - min(x)).days)    
            ).reset_index()
        start_time = time.time()
        new_data[dataset].drop("fechaobservacion", axis = 'columns', inplace=True)
        new_data[dataset]["departamento"]=new_data[dataset]["departamento"].replace(dic_dep)
        new_data[dataset]["municipio"]=new_data[dataset]["municipio"].replace(dic_mun)
        new_data[dataset].loc[(new_data[dataset]["municipio"]=="EL CARMEN") & (new_data[dataset]["departamento"]=="CHOCÓ"),"municipio"]="EL CARMEN DE ATRATO"
        new_data[dataset].loc[(new_data[dataset]["municipio"]=="SANTUARIO") & (new_data[dataset]["departamento"]=="ANTIOQUIA"),"municipio"]="EL SANTUARIO"
        new_data[dataset].loc[(new_data[dataset]["municipio"]=="EL CARMEN") & (new_data[dataset]["departamento"]=="SANTANDER"),"municipio"]="EL CARMEN DE CHUCURI"
        new_data[dataset]["DIVIPOLA"] = new_data[dataset].apply(
            lambda row: optain_divipola(row["departamento"],row["municipio"],divipola), axis=1)
        if dataset == "pressure":
            new_data[dataset].to_csv('datasets/pressure_daily_with_divipola.csv', mode='a', index=False, header=False)
        elif dataset == "temperature":
            new_data[dataset].to_csv('datasets/temperature_daily_with_divipola.csv', mode='a', index=False, header=False)
        print("--- %s seconds ---" % (time.time() - start_time))
        print(len(new_data[dataset]))
        del df
    result = client.close()
