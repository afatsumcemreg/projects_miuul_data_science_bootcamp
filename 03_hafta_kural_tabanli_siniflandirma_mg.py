
#############################################
# Kural Tabanlı Sınıflandırma ile Potansiyel Müşteri Getirisi Hesaplama
#############################################

#############################################
# İş Problemi
#############################################
# Bir oyun şirketi müşterilerinin bazı özelliklerini kullanarak seviye tabanlı (level based) yeni müşteri tanımları (persona)
# oluşturmak ve bu yeni müşteri tanımlarına göre segmentler oluşturup bu segmentlere göre yeni gelebilecek müşterilerin şirkete
# ortalama ne kadar kazandırabileceğini tahmin etmek istemektedir.

# Örneğin: Türkiye’den IOS kullanıcısı olan 25 yaşındaki bir erkek kullanıcının ortalama ne kadar kazandırabileceği belirlenmek isteniyor.


#############################################
# Veri Seti Hikayesi
#############################################
# Persona.csv veri seti uluslararası bir oyun şirketinin sattığı ürünlerin fiyatlarını ve bu ürünleri satın alan kullanıcıların bazı
# demografik bilgilerini barındırmaktadır. Veri seti her satış işleminde oluşan kayıtlardan meydana gelmektedir. Bunun anlamı tablo
# tekilleştirilmemiştir. Diğer bir ifade ile belirli demografik özelliklere sahip bir kullanıcı birden fazla alışveriş yapmış olabilir.

# Price: Müşterinin harcama tutarı
# Source: Müşterinin bağlandığı cihaz türü
# Sex: Müşterinin cinsiyeti
# Country: Müşterinin ülkesi
# Age: Müşterinin yaşı

################# Uygulama Öncesi #####################

#    PRICE   SOURCE   SEX COUNTRY  AGE
# 0     39  android  male     bra   17
# 1     39  android  male     bra   17
# 2     49  android  male     bra   17
# 3     29  android  male     tur   17
# 4     49  android  male     tur   17

################# Uygulama Sonrası #####################

#       customers_level_based        PRICE SEGMENT
# 0   BRA_ANDROID_FEMALE_0_18  1139.800000       A
# 1  BRA_ANDROID_FEMALE_19_23  1070.600000       A
# 2  BRA_ANDROID_FEMALE_24_30   508.142857       A
# 3  BRA_ANDROID_FEMALE_31_40   233.166667       C
# 4  BRA_ANDROID_FEMALE_41_66   236.666667       C


#############################################
# PROJE GÖREVLERİ
#############################################

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
pd.set_option('display.float_format', lambda x: '%.2f' % x)

#############################################
# GÖREV 1: Aşağıdaki soruları yanıtlayınız.
#############################################

# Soru 1: persona.csv dosyasını okutunuz ve veri seti ile ilgili genel bilgileri gösteriniz.
df = pd.read_csv("01_python_programming_for_data_science/01_python_alistirmalar_odev/3_hafta/persona.csv")

def check_df(dataframe, head=5):
    print(dataframe.head(head))
    print(dataframe.tail(head))
    print(dataframe.shape)
    print(dataframe.info())
    print(dataframe.columns)
    print(dataframe.isnull().values.any())
    print(dataframe.isnull().sum())
    print(dataframe.describe([0.05, 0.1, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99, 1]).T)

check_df(df)

# Soru 2: Kaç unique SOURCE vardır? Frekansları nedir?
df['SOURCE'].nunique()  # 2
df['SOURCE'].unique()  # array(['android', 'ios'], dtype=object)
df['SOURCE'].value_counts()
sns.countplot(x=df['SOURCE'])
plt.show(block=True)

# Soru 3: Kaç unique PRICE vardır?
df['PRICE'].nunique()    # 6
df['PRICE'].unique()    # array([39, 49, 29, 19, 59,  9], dtype=int64)

# Soru 4: Hangi PRICE'dan kaçar tane satış gerçekleşmiş?
df['PRICE'].value_counts()
sns.countplot(x=df['PRICE'])
plt.show(block=True)

# Soru 5: Hangi ülkeden kaçar tane satış olmuş?
df['COUNTRY'].value_counts()
df['COUNTRY'].nunique()

# Soru 6: Ülkelere göre satışlardan toplam ne kadar kazanılmış?
df.groupby('COUNTRY').agg({'PRICE': 'sum'})

# Soru 7: SOURCE türlerine göre göre satış sayıları nedir?
df.groupby('SOURCE').agg({'PRICE': 'count'})

# Soru 8: Ülkelere göre PRICE ortalamaları nedir?
df.groupby('COUNTRY').agg({'PRICE': 'mean'})

# Soru 9: SOURCE'lara göre PRICE ortalamaları nedir?
df.groupby('SOURCE').agg({'PRICE': 'mean'})

# Soru 10: COUNTRY-SOURCE kırılımında PRICE ortalamaları nedir?
df.groupby(['COUNTRY', 'SOURCE']).agg({'PRICE': 'mean'})

#############################################
# GÖREV 2: COUNTRY, SOURCE, SEX, AGE kırılımında ortalama kazançlar nedir?
#############################################
df.groupby(['COUNTRY', 'SOURCE', 'SEX', 'AGE']).agg({'PRICE': 'mean'})

#############################################
# GÖREV 3: Çıktıyı PRICE'a göre sıralayınız.
#############################################
# Önceki sorudaki çıktıyı daha iyi görebilmek için sort_values metodunu azalan olacak şekilde PRICE'a uygulayınız.
# Çıktıyı agg_df olarak kaydediniz.
age_df = df.groupby(['COUNTRY', 'SOURCE', 'SEX', 'AGE']).agg({'PRICE': 'mean'}).sort_values('PRICE', ascending=False)

#############################################
# GÖREV 4: Indekste yer alan isimleri değişken ismine çeviriniz.
#############################################
# Üçüncü sorunun çıktısında yer alan PRICE dışındaki tüm değişkenler index isimleridir.
# Bu isimleri değişken isimlerine çeviriniz.
# İpucu: reset_index()
# agg_df.reset_index(inplace=True)
age_df.reset_index(inplace=True)
age_df.head()

#############################################
# GÖREV 5: AGE değişkenini kategorik değişkene çeviriniz ve agg_df'e ekleyiniz.
#############################################
# Age sayısal değişkenini kategorik değişkene çeviriniz.
# Aralıkları ikna edici olacağını düşündüğünüz şekilde oluşturunuz.
# Örneğin: '0_18', '19_23', '24_30', '31_40', '41_70'
age_df['NEW_AGE'] = pd.cut(age_df['AGE'], bins=[0, 18, 23, 30, 40, 70], labels=['0_18', '19_23', '24_30', '31_40', '41_70'])
age_df.head()

#############################################
# GÖREV 6: Yeni level based müşterileri tanımlayınız ve veri setine değişken olarak ekleyiniz.
#############################################
# customers_level_based adında bir değişken tanımlayınız ve veri setine bu değişkeni ekleyiniz.
# Dikkat!
# list comp ile customers_level_based değerleri oluşturulduktan sonra bu değerlerin tekilleştirilmesi gerekmektedir.
# Örneğin birden fazla şu ifadeden olabilir: USA_ANDROID_MALE_0_18
# Bunları groupby'a alıp price ortalamalarını almak gerekmektedir.
age_df.drop(['AGE', 'PRICE'], axis=1).values
age_df['CUSTOMERS_LEVEL_BASED'] = ['_'.join(col) for col in age_df.drop(['AGE', 'PRICE'], axis=1).values]
age_df.head()

age_df = age_df.groupby('CUSTOMERS_LEVEL_BASED').agg({'PRICE': 'mean'})
age_df.reset_index(inplace=True)
age_df.head()
age_df.shape

#############################################
# GÖREV 7: Yeni müşterileri (USA_ANDROID_MALE_0_18) segmentlere ayırınız.
#############################################
# PRICE'a göre segmentlere ayırınız,
# segmentleri "SEGMENT" isimlendirmesi ile agg_df'e ekleyiniz,
# segmentleri betimleyiniz,

age_df['SEGMENT'] = pd.qcut(age_df['PRICE'], 4, labels=['D', 'C', 'B', 'A'])
age_df.head()

#############################################
# GÖREV 8: Yeni gelen müşterileri sınıflandırınız ne kadar gelir getirebileceğini tahmin ediniz.
#############################################
# 33 yaşında ANDROID kullanan bir Türk kadını hangi segmente aittir ve ortalama ne kadar gelir kazandırması beklenir?
new_user = 'tur_android_female_31_40'
age_df[age_df['CUSTOMERS_LEVEL_BASED'] == new_user]

# 35 yaşında IOS kullanan bir Fransız kadını hangi segmente ve ortalama ne kadar gelir kazandırması beklenir?
new_user = 'fra_ios_female_31_40'
age_df[age_df['CUSTOMERS_LEVEL_BASED'] == new_user]

# Türkiye’den IOS kullanıcısı olan 25 yaşındaki bir erkek kullanıcının ortalama ne kadar gelir kazandır?
new_user = 'tur_ios_male_24_30'
age_df[age_df['CUSTOMERS_LEVEL_BASED'] == new_user]