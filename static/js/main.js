// main.js - small UI helpers
document.addEventListener('DOMContentLoaded', () => {
  const uploadBtn = document.getElementById('uploadBtn');
  const fileInput = document.getElementById('fileInput');
  if(uploadBtn){
    uploadBtn.addEventListener('click', () => fileInput.click());
  }
  // preview
  if(fileInput){
    fileInput.addEventListener('change', () => {
      const p = document.getElementById('fileName');
      if(fileInput.files.length) p.textContent = fileInput.files[0].name;
      else p.textContent = 'No file selected';
    });
  }
  // BMI calculator (home page)
  const bmiCalc = document.getElementById('bmi_calc');
  if(bmiCalc){
    bmiCalc.addEventListener('click', () => {
      const hEl = document.getElementById('bmi_height');
      const wEl = document.getElementById('bmi_weight');
      const res = document.getElementById('bmi_result');
      const h = parseFloat(hEl.value);
      const w = parseFloat(wEl.value);
      if(!h || !w){ res.textContent = 'Enter height and weight'; return; }
      // height in meters
      const hm = h/100.0;
      const bmi = w / (hm*hm);
      const bmiRounded = Math.round(bmi*10)/10;
      let cat = '';
      if(bmi < 18.5) cat = 'Underweight';
      else if(bmi < 25) cat = 'Normal';
      else if(bmi < 30) cat = 'Overweight';
      else cat = 'Obese';
      res.textContent = bmiRounded + ' — ' + cat;
    });
  }
});
