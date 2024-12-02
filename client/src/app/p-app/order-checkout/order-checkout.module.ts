import { NgModule, CUSTOM_ELEMENTS_SCHEMA, NO_ERRORS_SCHEMA, } from "@angular/core";
import { CommonModule } from '@angular/common';
import { OrderCheckoutComponent } from "./order-checkout.component";
import { PLayoutModule } from "../p-layout/p-layout.module";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { TextBoxModule } from '@progress/kendo-angular-inputs';
import { ButtonsModule } from '@progress/kendo-angular-buttons';

@NgModule({
    declarations: [
        OrderCheckoutComponent
    ],
    imports: [
        CommonModule,
        PLayoutModule,
        FormsModule,
        ReactiveFormsModule,
        TextBoxModule,
        ButtonsModule
    ],
    schemas: [CUSTOM_ELEMENTS_SCHEMA, NO_ERRORS_SCHEMA],
    exports: [OrderCheckoutComponent],
})
export class OrderCheckoutModule { }