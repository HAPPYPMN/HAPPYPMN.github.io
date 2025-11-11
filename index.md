---
layout: default
title: Home
lang: en
---

<div class="profile-container">
  <div class="profile-pic">
    <img src="/assets/images/1.jpg" alt="Minnan Pei">
  </div>
  <div class="profile-text">
    <h1>Minnan Pei</h1>
    <p><strong>PhD student</strong><br>
    CASIA, UCAS<br>
    Beijing, China</p>
    
  <p>
    My research focuses on efficient computing for artificial intelligence algorithms and hardware-software co-optimization, with a particular emphasis on accelerating 3D Gaussian Splatting (3DGS). I am currently conducting academic research at <a href="http://clab.ia.ac.cn">CLab</a>, under the guidance of <a href="https://people.ucas.ac.cn/~chengjian">Prof. Jian Cheng</a> and Prof. Gang Li.
  </p><p>
    I graduated from the University of Chinese Academy of Sciences (UCAS) with a degree in Electronic Information Engineering, where I also served as the class monitor of the School of Electronics. During my studies, I was honored with the <a href="https://onestop.ucas.ac.cn/home/infob/48d6092a-be91-442a-adcf-50953a455869/0">Beijing Outstanding Student Award</a>, <a href="https://bkjy.ucas.ac.cn/index.php/2020-11-10-07-29-19/2020-11-10-07-32-02/6979-2019-9">Beijing Distinguished Graduate Award</a>, and <a href="https://bkjy.ucas.edu.cn/index.php/tzgg/6433-2021-2050">the National Scholarship</a>. Additionally, I served as the President of the Student Union of the School of Artificial Intelligence during my graduate studies.
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

<h2 id="publications">Research</h2>

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
