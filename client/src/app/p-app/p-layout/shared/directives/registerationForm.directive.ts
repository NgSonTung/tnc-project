import { AbstractControl, ValidationErrors, ValidatorFn } from "@angular/forms";

export const confirmPassword: ValidatorFn = (control: AbstractControl) : ValidationErrors | null => {
    const password = control.get('Password');
    const confirmPassword = control.get('ConfirmPassword');

    return password?.value === confirmPassword?.value ? { notmatched: true} : null;
};