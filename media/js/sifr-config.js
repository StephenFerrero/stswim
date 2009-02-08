var hasty = {
  src: '/media/flash/hasty.swf'
  ,ratios: [11, 1.49, 13, 1.41, 16, 1.39, 19, 1.38, 25, 1.37, 26, 1.36, 41, 1.35, 52, 1.34, 54, 1.33, 55, 1.34, 81, 1.33, 83, 1.32, 84, 1.33, 1.32]
};

var babel = {
  src: '/media/flash/babelfish.swf'
  ,ratios: [8, 0.98, 13, 0.94, 17, 0.89, 18, 0.86, 23, 0.87, 28, 0.85, 36, 0.83, 37, 0.82, 41, 0.83, 55, 0.82, 56, 0.81, 57, 0.82, 91, 0.81, 93, 0.8, 96, 0.81, 99, 0.8, 101, 0.81, 105, 0.8, 106, 0.81, 0.8]
};

sIFR.activate(hasty);

sIFR.replace(babel, {
  selector: 'h1, h2'
  ,css: [
      '.sIFR-root { color: #000066; }'
	  ,'a { color: #000066; text-decoration: none; }'
      ,'a:link, a:visited { color: #000066; }'
      ,'a:hover { color: #2fbdd6; }'
      ,'.monthtitle { text-align: center; width: 300px; }'
    ]
   ,wmode: 'transparent'
   
});

sIFR.replace(hasty, {
  selector: '#navbar li'
  ,css: [
      '.sIFR-root { font-size: 18; text-align: center;}'
	  ,'a { text-decoration: none; }'
      ,'a:link { color: #000000; }'
      ,'a:hover { color: #000000; }'
    ]
  ,wmode: 'transparent'
  ,selectable: false
  ,tuneHeight: 65
  ,offsetTop: 35
  ,forceWidth: 45
});
