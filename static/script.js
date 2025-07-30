function openLightbox(src) {
  const lb = document.getElementById('lightbox');
  const img = document.getElementById('lightbox-img');
  img.src = src;
  lb.style.display = 'flex';
}
function closeLightbox() {
  document.getElementById('lightbox').style.display = 'none';
}

const box = document.querySelector("#box");
let i = 0;

// Text
let text = `Welcome to Palashbaria Secondary School! We are dedicated to providing quality education and fostering a supportive learning environment. Explore our website to learn more about our programs, faculty, and community activities.`;

// Autotyping function specified for text variable
const autoType = ()=>{
    text.split("");
    box.innerHTML+=text[i];
    if(i == (text.length-1)){
        clearInterval(m);
    }
    i++;
}

// Setting Intervals
const m = setInterval(autoType,100);
