const DTOProduct = require("../Default/DTOProduct");
module.exports = class DTOProductCustomize extends DTOProduct {
  constructor(data) {
    super(data);
    this.BrandName = data.BrandName ?? null;
    this.Base64Image = data.Base64Image ?? null;
    this.RatingAvg = data.RatingAvg ?? 0;
  }
};
