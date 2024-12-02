module.exports = class DTOFeature {
  constructor(data) {
    this.FeatureID = data.FeatureID;
    this.Feature = data.Feature ?? null;
    this.ProductID = data.ProductID ?? null;
    if (!data.CreatedAt) data.CreatedAt = new Date().toISOString();
    this.CreatedAt = data.CreatedAt;
  }
};
