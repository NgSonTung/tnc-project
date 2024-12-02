const fs = require("fs");
const path = require("path");

exports.convertImageToBase64 = async (imageName, baseUrl = null) => {
  let result;

  const dirPath = path.join(
    __dirname,
    "..",
    "dev-Data",
    "productImages"
    // imageName + ".jpg"
  );

  const files = await fs.promises.readdir(dirPath);
  const matchingFile = files.find((file) => file.startsWith(imageName));

  if (matchingFile) {
    const imagePath = path.join(dirPath, matchingFile);
    const imageData = await fs.promises.readFile(imagePath, "base64");
    result = {Url: `${baseUrl}/${imageName}`, Base64: imageData};
  } else {
    result = {Url: `${baseUrl}/${imageName}`, Base64: null};
  }
  return result;
};
