export class DTOBrand {
  BrandID: number;
  BrandName: string;
  CreateAt: string;

  constructor(brandID: number, brandName: string, createAt: string) {
    this.BrandID = brandID;
    this.BrandName = brandName;
    this.CreateAt = createAt;
  }
}
