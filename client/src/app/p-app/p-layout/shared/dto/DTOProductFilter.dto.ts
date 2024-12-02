export interface DTOFilterPrice {
    gte?: number | string,
    lte?: number | string,
    eq?: number | string
}

export interface DTOProductFilter {
    Name?: string,
    Price?: DTOFilterPrice,
    BrandID?: number,
    CategoryID?: number
    PageSize?: Number,
    Page?: number
}