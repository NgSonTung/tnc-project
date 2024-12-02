import { NgModule, CUSTOM_ELEMENTS_SCHEMA, NO_ERRORS_SCHEMA, } from "@angular/core";
import { CommonModule } from '@angular/common';
import { PLayoutModule } from "../p-layout/p-layout.module";
import { TncProfileComponent } from "./tnc-profile.component";
import { LayoutModule } from '@progress/kendo-angular-layout';
import { OrderHistoryComponent } from "./order-history/order-history.component";
import { PersonalInfoComponent } from "./personal-info/personal-info.component";
import { TncProfileRoutingModule } from "./tnc-profile-routing.module";
import { DateInputsModule } from '@progress/kendo-angular-dateinputs';
import { GridModule } from '@progress/kendo-angular-grid';
import { ButtonsModule } from '@progress/kendo-angular-buttons';
import { InputsModule } from '@progress/kendo-angular-inputs';
import { LabelModule } from '@progress/kendo-angular-label';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ChangePasswordComponent } from './change-password/change-password.component';
import { IconModule } from '@progress/kendo-angular-icons';

@NgModule({
    declarations: [TncProfileComponent, OrderHistoryComponent, PersonalInfoComponent, ChangePasswordComponent],
    imports: [
        CommonModule,
        PLayoutModule,
        LayoutModule,
        TncProfileRoutingModule,
        DateInputsModule,
        GridModule,
        ButtonsModule,
        InputsModule,
        LabelModule,
        FormsModule,
        ReactiveFormsModule,
        IconModule
    ],
    schemas: [CUSTOM_ELEMENTS_SCHEMA, NO_ERRORS_SCHEMA],
    exports: [TncProfileComponent],
})
export class TncProfileModule { }