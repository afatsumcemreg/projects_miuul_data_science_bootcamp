###############################################
# Python Alıştırmalar
###############################################

###############################################
# GÖREV 1: Veri yapılarının tipleriniz inceleyiniz.
###############################################

x = 8
type(x)

y = 3.2
type(y)

z = 8j + 18
type(z)

a = "Hello World"
type(a)

b = True
type(b)

c = 23 < 22
type(c)

l = [1, 2, 3, 4, "String", 3.2, False]
type(l)

d = {"Name": "Jake",
     "Age": [27, 56],
     "Adress": "Downtown"}
type(d)

t = ("Machine Learning", "Data Science")
type(t)

s = {"Python", "Machine Learning", "Data Science", "Python"}
type(s)

###############################################
# GÖREV 2: Verilen string ifadenin tüm harflerini büyük harfe çeviriniz. Virgül ve nokta yerine space koyunuz, kelime kelime ayırınız.
###############################################

text = "The goal is to turn data into information, and information into insight."
text = text.upper().replace('.', ' ').replace(',', ' ').split()

###############################################
# GÖREV 3: Verilen liste için aşağıdaki görevleri yapınız.
###############################################

lst = ["D", "A", "T", "A", "S", "C", "I", "E", "N", "C", "E"]

# Adım 1: Verilen listenin eleman sayısına bakın.
len(lst)

# Adım 2: Sıfırıncı ve onuncu index'teki elemanları çağırın.
lst[0]
lst[-1]

# Adım 3: Verilen liste üzerinden ["D","A","T","A"] listesi oluşturun.
lst[0:4]

# Adım 4: Sekizinci index'teki elemanı silin.
lst.pop(8)

# Adım 5: Yeni bir eleman ekleyin.
lst.append('X')

# Adım 6: Sekizinci index'e  "N" elemanını tekrar ekleyin.
lst.insert(8, 'N')

###############################################
# GÖREV 4: Verilen sözlük yapısına aşağıdaki adımları uygulayınız.
###############################################

dict = {'Christian': ["America", 18],
        'Daisy': ["England", 12],
        'Antonio': ["Spain", 22],
        'Dante': ["Italy", 25]}

# Adım 1: Key değerlerine erişiniz.
dict.keys()

# Adım 2: Value'lara erişiniz.
dict.values()

# Adım 3: Daisy key'ine ait 12 değerini 13 olarak güncelleyiniz.
dict['Daisy'][1] = 13

# Adım 4: Key değeri Ahmet value değeri [Turkey,24] olan yeni bir değer ekleyiniz.
dict.update({'Ahmet': ['Turkey', 24]})

# Adım 5: Antonio'yu dictionary'den siliniz.
dict.pop('Antonio')

###############################################
# GÖREV 5: Arguman olarak bir liste alan, listenin içerisindeki tek ve çift sayıları ayrı listelere atıyan ve bu listeleri return eden fonskiyon yazınız.
###############################################

lst = [2, 13, 18, 93, 22]


def odd_even_numbers(list_store):
    odd_numbers, even_numbers = [], []
    for num in list_store:
        if num % 2 == 0:
            even_numbers.append(num)
        else:
            odd_numbers.append(num)
    return odd_numbers, even_numbers


odd_list, even_list = odd_even_numbers(lst)


# diger bir cozum
def odd_even_num(list):
    return [i for i in list if i % 2 == 0], [i for i in list if i % 2 != 0]


even, odd = odd_even_num(lst)

###############################################
# GÖREV 6: Aşağıda verilen listede mühendislik ve tıp fakülterinde dereceye giren öğrencilerin isimleri bulunmaktadır.
# Sırasıyla ilk üç öğrenci mühendislik fakültesinin başarı sırasını temsil ederken son üç öğrenci de tıp fakültesi öğrenci sırasına aittir.
# Enumarate kullanarak öğrenci derecelerini fakülte özelinde yazdırınız.
###############################################

students = ["Ali", "Veli", "Ayse", "Talat", "Zeynep", "Ece"]

# Solution_1_for_loop

for index, student in enumerate(students, 1):
    if index < 4:
        print(f'Muhendislik Fakultesi: {index}. ogrenci: {student}')
    else:
        print(f'Tip Fakultesi {index - 3}. ogrenci: {student}')

# Solution_2_list_comprehension

student_list = [f'Muhendislik Fakultesi: {index}. ogrenci: {student}' if index < 4 else f'Tip Fakultesi {index - 3}. ogrenci: {student}' for index, student in enumerate(students, 1)]
for i in student_list:
    print(i)

###############################################
# GÖREV 7: Aşağıda 3 adet liste verilmiştir. Listelerde sırası ile bir dersin kodu, kredisi ve kontenjan bilgileri yer almaktadır. Zip kullanarak ders bilgilerini bastırınız.
###############################################

ders_kodu = ["CMP1005", "PSY1001", "HUK1005", "SEN2204"]
kredi = [3, 4, 2, 4]
kontenjan = [30, 75, 150, 25]

course_info = list(zip(kredi, ders_kodu, kontenjan))

# Solution_1_for_loop
for i in course_info:
    print(f'Kredisi {i[0]} olan {i[1]} kodlu dersin konetenjani {i[2]} kisidir.')

# Solution_2_list_comprehension
[f'Kredisi {i[0]} olan {i[1]} kodlu dersin konetenjani {i[2]} kisidir.' for i in course_info]


###############################################
# GÖREV 8: Aşağıda 2 adet set verilmiştir.
# Sizden istenilen eğer 1. küme 2. kümeyi kapsiyor ise ortak elemanlarını eğer kapsamıyor ise 2. kümenin 1. kümeden farkını yazdıracak fonksiyonu tanımlamanız beklenmektedir.
###############################################

def superset_kume(set1, set2):
    if set1.issuperset(set2):
        print(set2.intersection(set1))
    else:
        print(set2.difference(set1))


kume1 = set(["data", "python"])
kume2 = set(["data", "function", "qcut", "lambda", "python", "miuul"])
superset_kume(kume1, kume2)

###########################################################################################
# BONUS SORU: Verilen listeden en düşük nota sahip kişilerin adlarını alfabetik sıraya göre yazınız. Liste sırasıyla öğrenci ve aldığı notu ifade etmektedir.
# Not: Listedeki kişi sayısı değişiklik gösterebilir, birden fazla en düşük not veya en düşük ikinci nota sahip kişiler olabilir.
# Beklenen çıktı
    # Berry
    # Harry
###########################################################################################

    # 1. solution
nlis = ['Harry', 37.21, 'Berry', 37.21, 'Tina', 37.2, 'Akriti', 41.0, 'Harsh', 39.20]

a, b = [], []
[a.append(x) if i % 2 == 0 else b.append(x) for i, x in enumerate(nlis)]
student = dict(zip(a, b))
names = [i for i, k in student.items() if k == sorted(set(student.values()))[1]]
for i in sorted(names):
    print(i)

    # second solution
def student(scores):
    return [scores[i] for i in range(len(scores)) if i % 2 == 0], [scores[i] for i in range(len(scores)) if i % 2 != 0]

keys, values = student(nlis)
new_list = dict(zip(keys, values))

names = sorted([i for i, k in new_list.items() if k == sorted(set(new_list.values()))[1]])
for i in names:
    print(i)