const ProductDAO = require("../DAO/ProductDAO");
const CategoryDAO = require("../DAO/CategoryDAO");
// const ProductSchema = require("../model/Product");
const ImageUtils = require("../utils/ImageUtils");
const path = require("path");
const fs = require("fs");
const DTOProduct = require("../DTO/Default/DTOProduct");
exports.getProducts = async (req, res) => {
  let reqHeader = req.headers;
  try {
    const products = await ProductDAO.getAllProducts(reqHeader);
    if (products.TotalProduct == 0) {
      res.status(500).json({
        Code: 500,
        Msg: `Product not found !!!`,
      });
    } else {
      res.status(200).json({
        Code: 200,
        Msg: null,
        Page: products.Page,
        PageSize: products.PageSize,
        TotalPage: products.TotalPage,
        TotalProduct: products.TotalProduct,
        Data: products.DataProducts,
      });
    }
  } catch (err) {
    res.status(500).json({
      Code: 500,
      Msg: `FAIL with ${err.toString()}`,
    });
  }
};

exports.getProductById = async (req, res) => {
  // console.log("req.params", req.params);
  try {
    const id = req.params.id * 1;
    const product = await ProductDAO.getProductById(id);
    if (!product) {
      return res
        .status(404) //NOT FOUND
        .json({
          Code: 404,
          Msg: `Not found product with Id ${id}!`,
        });
    }
    return res.status(200).json({
      Code: 200,
      Msg: null,
      Data: product,
    });
  } catch (e) {
    console.log(e);
    return res.status(500).json({
      Code: 500,
      Msg: e.toString(),
    });
  }
};

exports.createNewProduct = async (req, res) => {
  const newProduct = req.body;
  const dto = new DTOProduct(newProduct);
  try {
    let product = await ProductDAO.getProductByName(dto.Name);
    if (product) {
      return res
        .status(403) //Forbidden
        .json({
          Code: 403,
          Msg: `Product name duplicate!`,
        });
    }
    await ProductDAO.createNewProduct(dto);
    product = await ProductDAO.getProductByName(dto.Name);
    product && (await ProductDAO.createNewRating(product));
    // console.log(`Created new product successfully!`);
    return res.status(200).json({
      Code: 200,
      Msg: null,
      Data: product,
    });
  } catch (e) {
    console.log(e);
    res.status(500).json({
      Code: 500,
      Msg: `Product create failed ${e.toString()}`,
    });
  }
};

exports.deleteById = async (req, res) => {
  try {
    const id = req.params.id * 1;
    const product = await ProductDAO.getProductById(id);
    if (!product) {
      return res
        .status(404) //NOT FOUND
        .json({
          Code: 404,
          Msg: `Product with Id ${id} not found!`,
        });
    }
    await ProductDAO.deleteProductById(id);
    return res.status(200).json({
      Code: 200,
      Msg: null,
    });
  } catch (e) {
    console.log(e);
    return res.status(500).json({
      Code: 500,
      Msg: e.toString(),
    });
  }
};

exports.deleteMultipleProductById = async (req, res) => {
  const idList = req.query.id;
  try {
    if (!idList || idList.length === 0) {
      return res.status(403).json({
        Code: 403,
        Msg: `Invalid ids`,
      });
    }
    await ProductDAO.deleteMultipleProductById(idList);
    return res.status(200).json({
      Code: 200,
      Msg: null,
    });
  } catch (e) {
    console.log(e);
    return res.status(500).json({
      Code: 500,
      Msg: `Delete products with id ${idList} failed! ${e.toString()}`,
    });
  }
};

exports.getProductNonPaginate = async (req, res) => {
  try {
    const products = await ProductDAO.getProductsNotPagination(req.query);
    if (!products) {
      return res
        .status(404) //NOT FOUND
        .json({
          Code: 404,
          Msg: `Products list not found!`,
        });
    }
    return res.status(200).json({
      Code: 200,
      Msg: null,
      Data: products,
    });
  } catch (e) {
    console.log(e);
    return res.status(500).json({
      Code: 500,
      Msg: e.toString(),
    });
  }
};

exports.updateProductById = async (req, res) => {
  // console.log("Id update", req.params.id);
  try {
    const id = req.params.id * 1;
    const updateInfo = req.body;
    let product = await ProductDAO.getProductById(id);
    if (!product) {
      return res.status(404).json({
        Code: 404,
        Msg: `Not found product with Id ${id}!`,
      });
    }
    await ProductDAO.updateProductById(id, updateInfo);
    product = await ProductDAO.getProductById(id);
    return res.status(200).json({
      Code: 200,
      Msg: null,
      Data: product,
    });
  } catch (e) {
    console.log(e);
    res.status(500).json({
      Code: 500,
      Msg: `Update product with id: ${id} failed! ${e.toString()}`,
    });
  }
};

exports.getFileProductImage = async (req, res) => {
  let imageName = req.params.imageName;
  const baseUrl = `${req.protocol}://${req.get(
    "host"
  )}/api/images/subImgimages/`;
  const result = await ImageUtils.convertImageToBase64(imageName, baseUrl);
  // console.log(result);
  res.status(200).json({
    Data: result,
  });
};

exports.saveFileProductImage = async (req, res) => {
  try {
    let info = JSON.parse(req.body.body);
    const imagePath = path.join(
      __dirname,
      "..",
      "dev-Data",
      "productImages",
      info.ImageName + ".jpg"
    );
    const file = req.file;
    console.log(file);
    console.log(imagePath);

    const imageBuffer = await fs.promises.readFile(file.path);
    const base64Image = imageBuffer.toString("base64");
    const buffer = Buffer.from(base64Image, "base64");
    fs.writeFile(imagePath, buffer, (err) => {
      if (err) {
        // console.error(err);
        res.status(500).json({Code: 500, Msg: "Failed to save the file."});
      }
    });
    const Name = info.ImageName;
    console.log("name", Name);
    img = {
      Image: Name,
    };
    await ProductDAO.updateProductById(info.ProductID, img);
    console.log("File saved successfully.");
    res.status(200).json({Code: 200, Msg: "File saved successfully."});
  } catch (e) {
    console.log(e);
    res.status(500).json({error: `Failed to save the file. ${e.toString()}`});
  }
};
