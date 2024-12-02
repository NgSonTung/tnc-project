import { HttpEvent, HttpHandler, HttpInterceptor, HttpRequest } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { AuthService } from "../http-interceptors/auth.service";
import { Observable } from "rxjs";

@Injectable()
export class JWTInterceptor implements HttpInterceptor {
    constructor(private authenService: AuthService) {}

    intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
        // add authorization header with jwt token if available
        let currentUser = this.authenService.currentUserValue;
        if (currentUser && currentUser.Token) {
            req = req.clone({
                setHeaders: {
                    Authorization: `Bearer ${currentUser.Token}`
                }
            }) 
        }

        return next.handle(req);
    }
}