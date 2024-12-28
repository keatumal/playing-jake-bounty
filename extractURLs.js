const links = document.querySelectorAll('a._font-pub-headings_h3mln_124')
const urls = []
links.forEach(link => urls.push(link.getAttribute('href')))
console.log(urls.join('\n'))