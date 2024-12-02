export class DTOFeature {
  FeatureID: number;
  Feature: string;
  ProductID: number;
  CreateAt: string;

  constructor(
    featureID: number,
    feature: string,
    productID: number,
    createAt: string
  ) {
    this.FeatureID = featureID;
    this.Feature = feature;
    this.ProductID = productID;
    this.CreateAt = createAt;
  }
}
