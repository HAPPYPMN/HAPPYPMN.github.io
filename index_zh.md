---
layout: default
title: 主页
lang: zh
---

<div class="profile-container">
  <div class="profile-pic">
    <img src="/assets/images/1.jpg" alt="Minnan Pei">
  </div>
  <div class="profile-text">
    <h1>裴旻楠</h1>
    <p><strong>在读博士研究生</strong><br>
    自动化研究所, 中国科学院大学<br>
    北京, 中国</p>
    
<p>
    我的研究聚焦于人工智能算法的高效计算与软硬件协同优化，特别是对三维高斯溅射（3D Gaussian Splatting, 3DGS）的加速。我目前在<a href="http://clab.ia.ac.cn">CLab</a>实验室进行学术研究，导师为<a href="https://people.ucas.ac.cn/~chengjian">程健研究员</a>和李钢研究员。
  </p><p>
    我毕业于中国科学院大学电子信息工程专业，并曾担任电子学院本科班班长。在校期间，我荣获<a href="https://onestop.ucas.ac.cn/home/infob/48d6092a-be91-442a-adcf-50953a455869/0">北京市三好学生</a>、<a href="https://bkjy.ucas.ac.cn/index.php/2020-11-10-07-29-19/2020-11-10-07-32-02/6979-2019-9">北京市优秀毕业生</a>以及<a href="https://bkjy.ucas.edu.cn/index.php/tzgg/6433-2021-2050">国家奖学金</a>。此外，研究生期间我曾担任人工智能学院学生会主席。
  </p>

    <div class="contact-links">
      {% assign contacts = site.data.contacts %}
      {% if contacts %}
        {% for contact in contacts %}
          {% assign contact_label = contact.label[page.lang] | default: contact.label.en | default: contact.label %}
          <a href="{{ contact.url }}" {% if contact.new_tab %}target="_blank"{% endif %}>{{ contact_label }}</a>{% unless forloop.last %}/ {% endunless %}
        {% endfor %}
      {% endif %}
      <!-- <a href="[你的GitHub链接]" target="_blank">GitHub</a> /  -->
      <!-- <a href="[你的CV文件链接]" target="_blank">下载 CV</a> -->
    </div>
  </div>
</div>

<h2 id="publications">研究</h2>

<ul class="publications-list">
  {% assign publications = site.data.publications %}
  {% assign resource_labels = site.data.resource_labels %}
  {% assign current_labels = resource_labels[page.lang] | default: resource_labels.en %}
  {% for publication in publications %}
  <li>
    <p> {{ publication.authors }} "{{ publication.title }}". <em>{{ publication.venue }}</em>, {{ publication.year }}.</p>
    {% if publication.resources %}
    <div class="resource-links">
      {% for resource in publication.resources %}
        {% assign resource_label = resource.label %}
        {% if resource_label == nil %}
          {% assign resource_label = current_labels[resource.type] | default: resource.type %}
        {% endif %}
        <a href="{{ resource.url }}" {% unless resource.new_tab == false %}target="_blank"{% endunless %}>{{ resource_label }}</a>
      {% endfor %}
    </div>
    {% endif %}
  </li>
  {% endfor %}
</ul>
