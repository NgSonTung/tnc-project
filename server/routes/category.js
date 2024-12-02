const express = require("express");
const categoryController = require("../controllers/Category");
const router = express.Router();

router.route("/").get(categoryController.getAllCategories);
// router.route("/:id").get(categoryController.getCategoryById);

module.exports = router;
