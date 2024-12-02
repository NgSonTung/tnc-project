const express = require("express");
const productController = require("../Controllers/Product");
const authController = require("../Controllers/auth");
const StaticData = require("../utils/StaticData");
const router = express.Router();
const multer = require("multer");
router
  .route("/")
  .get(productController.getProducts)
  .post(
    authController.protect,
    authController.restrictTo(StaticData.AUTH.Role.admin),
    productController.createNewProduct
  )
  .delete(
    authController.protect,
    authController.restrictTo(StaticData.AUTH.Role.admin),
    productController.deleteMultipleProductById
  );

router
  .route("/productnonpagination")
  .get(productController.getProductNonPaginate);

router
  .route("/:id")
  .get(productController.getProductById)
  .delete(
    authController.protect,
    authController.restrictTo(StaticData.AUTH.Role.admin),
    productController.deleteById
  )
  .patch(
    authController.protect,
    authController.restrictTo(StaticData.AUTH.Role.admin),
    productController.updateProductById
  );
const upload = multer({dest: "../dev-data/productImages"});
router
  .route("/image")
  .post(
    authController.protect,
    authController.restrictTo(StaticData.AUTH.Role.admin),
    upload.single("file"),
    productController.saveFileProductImage
  );
router.route("/image/:imageName").get(productController.getFileProductImage);

// router.route("/saveFileImage").post(productController.saveFileImage);
module.exports = router;
