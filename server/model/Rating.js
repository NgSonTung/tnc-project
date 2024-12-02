const ModelSchema = require("./ModelSchema");
const ModelSchemaValidator = require("./ModelSchemaValidator");
const sql = require("mssql");

const RatingSchema = new ModelSchema(
  {
    RatingID: new ModelSchemaValidator({
      name: "RatingID",
      sqlType: sql.Int,
    }),
    _5star: new ModelSchemaValidator({
      name: "_5star",
      sqlType: sql.Int,
      require: true,
    }),
    _4star: new ModelSchemaValidator({
      name: "_4star",
      sqlType: sql.Int,
      require: true,
    }),
    _3star: new ModelSchemaValidator({
      name: "_3star",
      sqlType: sql.Int,
      require: true,
    }),
    _2star: new ModelSchemaValidator({
      name: "_2star",
      sqlType: sql.Int,
      require: true,
    }),
    _1star: new ModelSchemaValidator({
      name: "_1star",
      sqlType: sql.Int,
      require: true,
    }),
    ProductID: new ModelSchemaValidator({
      name: "ProductID",
      sqlType: sql.Int,
      require: true,
    }),
    CreatedAt: new ModelSchemaValidator({
      name: "CreatedAt",
      sqlType: sql.DateTime,
      default: new Date().toISOString(),
      require: true,
    }),
  },
  "Rating",
  "createdAt"
);
module.exports = RatingSchema;
