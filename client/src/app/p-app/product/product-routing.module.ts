import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { ProductListComponent } from './product-list/product-list.component';
import { ProductDetailComponent } from './product-detail/product-detail.component';

export const ProductRouting: Routes = [
    { path: ':productname', component: ProductDetailComponent }
];

@NgModule({
    imports: [RouterModule.forChild(ProductRouting)],
    exports: [RouterModule],
})
export class ProductRoutingModule { }
