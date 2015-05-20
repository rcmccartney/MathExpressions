input('Visualizing a subset of the data. Press Enter')
clf ;
imdbPath = fullfile('images', 'imdb.mat');

if exist(imdbPath, 'file')
  imdb = load(opts.imdbPath) ;
else
  top = 'images' ;
  files = dir(fullfile(top));
  fileNames = {files(~[files.isdir]).name};
  count = 1 ; 
  for k=1:length(fileNames),
      if mod(k,10) == 0, 
        images(:,:,count) = load(fullfile(top, fileNames{k})) ; 
        display(fileNames{k}) ;
        count = count + 1 ; 
      end;
      if count == 100,
          break
      end;
  end;
  shuffle = randperm(size(images,3));
  images = images(:,:,shuffle);
end

rows = [] ;
for i=1:size(images,3),
    rows = [rows ; reshape(images(:,:,i) ,1,[]) ] ;
end;
displayData(rows) ;

