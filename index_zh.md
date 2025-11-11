---
layout: default
title: 涓婚〉
lang: zh
---

<div class="profile-container">
  <div class="profile-pic">
    <img src="/assets/images/1.jpg" alt="Minnan Pei">
  </div>
  <div class="profile-text">
    <h1>瑁存椈妤?/h1>
    <p><strong>鍦ㄨ鍗氬＋鐮旂┒鐢?/strong><br>
    鑷姩鍖栫爺绌舵墍, 涓浗绉戝闄㈠ぇ瀛?br>
    鍖椾含, 涓浗</p>
    
<p>
    鎴戠殑鐮旂┒鑱氱劍浜庝汉宸ユ櫤鑳界畻娉曠殑楂樻晥璁＄畻涓庤蒋纭欢鍗忓悓浼樺寲锛岀壒鍒槸瀵逛笁缁撮珮鏂簠灏勶紙3D Gaussian Splatting, 3DGS锛夌殑鍔犻€熴€傛垜鐩墠鍦?a href="http://clab.ia.ac.cn">CLab</a>瀹為獙瀹よ繘琛屽鏈爺绌讹紝瀵煎笀涓?a href="https://people.ucas.ac.cn/~chengjian">绋嬪仴鐮旂┒鍛?/a>鍜屾潕閽㈢爺绌跺憳銆?
  </p><p>
    鎴戞瘯涓氫簬涓浗绉戝闄㈠ぇ瀛︾數瀛愪俊鎭伐绋嬩笓涓氾紝骞舵浘鎷呬换鐢靛瓙瀛﹂櫌鏈鐝彮闀裤€傚湪鏍℃湡闂达紝鎴戣崳鑾?a href="https://onestop.ucas.ac.cn/home/infob/48d6092a-be91-442a-adcf-50953a455869/0">鍖椾含甯備笁濂藉鐢?/a>銆?a href="https://bkjy.ucas.ac.cn/index.php/2020-11-10-07-29-19/2020-11-10-07-32-02/6979-2019-9">鍖椾含甯備紭绉€姣曚笟鐢?/a>浠ュ強<a href="https://bkjy.ucas.edu.cn/index.php/tzgg/6433-2021-2050">鍥藉濂栧閲?/a>銆傛澶栵紝鐮旂┒鐢熸湡闂存垜鏇炬媴浠讳汉宸ユ櫤鑳藉闄㈠鐢熶細涓诲腑銆?
  </p>

    <div class="contact-links">
      <a href="mailto:[peiminnan19@mails.ucas.ac.cn]">Email</a>/ 
      <a href="https://scholar.google.com/citations?hl=en&user=McR2_kgAAAAJ" target="_blank">Google Scholar</a>/ 
      <!-- <a href="[浣犵殑GitHub閾炬帴]" target="_blank">GitHub</a> /  -->
      <!-- <a href="[浣犵殑CV鏂囦欢閾炬帴]" target="_blank">涓嬭浇 CV</a> -->
    </div>
  </div>
</div>

<h2 id="publications">鐮旂┒</h2>

<ul class="publications-list">
  {% assign publications = site.data.publications %}
  {% for publication in publications %}
  <li>
    <p> {{ publication.authors }} "{{ publication.title }}". <em>{{ publication.venue }}</em>, {{ publication.year }}.</p>
    {% if publication.resources %}
    <div class="resource-links">
      {% for resource in publication.resources %}
        {% assign label = resource.label %}
        {% if label %}
          {% if label[page.lang] %}
            {% assign resource_label = label[page.lang] %}
          {% else %}
            {% assign resource_label = label %}
          {% endif %}
        {% else %}
          {% assign resource_label = "[Link]" %}
        {% endif %}
        <a href="{{ resource.url }}" {% if resource.new_tab != false %}target="_blank"{% endif %}>{{ resource_label }}</a>
      {% endfor %}
    </div>
    {% endif %}
  </li>
  {% endfor %}
</ul>

