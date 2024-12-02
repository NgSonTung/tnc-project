const express = require("express");
const brandController = require("../controllers/Brand");
const router = express.Router();

router.route("/").get(brandController.getAllBrands);
router.route("/:id").get(brandController.getBrandById);

module.exports = router;
