const sql = require("mssql");
const ModelSchemaValidator = require("./ModelSchemaValidator");
const ModelSchema = require("./ModelSchema");

const ProductSchema = new ModelSchema(
  {
    ProductID: new ModelSchemaValidator({
      name: "ProductID",
      sqlType: sql.Int,
    }),
    Stock: new ModelSchemaValidator({
      name: "Stock",
      sqlType: sql.Int,
    }),
    Name: new ModelSchemaValidator({
      name: "Name",
      sqlType: sql.NVarChar,
      require: true,
    }),
    Favorite: new ModelSchemaValidator({
      name: "Favorite",
      sqlType: sql.Int,
      require: true,
      validator: function (val) {
        return 0 || 1;
      },
    }),
    CategoryID: new ModelSchemaValidator({
      name: "CategoryID",
      sqlType: sql.Int,
      require: true,
    }),
    Price: new ModelSchemaValidator({
      name: "Price",
      sqlType: sql.Float,
      require: true,
    }),

    BrandID: new ModelSchemaValidator({
      name: "BrandID",
      sqlType: sql.Int,
      require: true,
    }),
    Image: new ModelSchemaValidator({
      name: "Image",
      sqlType: sql.NVarChar,
      require: true,
    }),
    Sale: new ModelSchemaValidator({
      name: "Sale",
      sqlType: sql.Float,
      default: "",
    }),
    Description: new ModelSchemaValidator({
      name: "Description",
      sqlType: sql.NVarChar,
      require: true,
      validator: function (val) {
        return val.length > 0;
      },
    }),
    CreatedAt: new ModelSchemaValidator({
      name: "CreatedAt",
      sqlType: sql.DateTime,
      default: new Date().toISOString(),
      require: true,
    }),
  },
  "Product",
  "price"
);
module.exports = ProductSchema;
