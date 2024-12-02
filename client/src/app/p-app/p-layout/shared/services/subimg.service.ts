import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { DTOPayment } from '../dto/DTOPayment';
import { DTOSubimg } from '../dto/DTOSubimg';
import { DTOSubImageResponse } from '../dto/DTOSubImage.dto';
import { environment } from 'src/app/environments/environments';

@Injectable({
  providedIn: 'root',
})
export class subImgService {
  constructor(private http: HttpClient) {
    console.log('subimg service started');
  }

  getData(
    page: number,
    pageSize: number,
    filterStr: string
  ): Observable<DTOSubimg> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('pageSize', pageSize.toString());
    return this.http
      .get<DTOSubimg>(`/api/v1/subimg/${filterStr}`, {
        params,
      })
      .pipe(catchError(this.handleError));
  }

  getDataById(id: number): Observable<DTOSubimg> {
    return this.http
      .get<DTOSubimg>(`/api/v1/subimg/${id}`)
      .pipe(catchError(this.handleError));
  }

  getProductSubImage(id: number): Observable<DTOSubImageResponse> {
    return this.http.get<DTOSubImageResponse>(`${environment.apiUrl}/subimg/product/${id}`).pipe(catchError(this.handleError));
  }

  createData(subimg: DTOPayment): Observable<DTOSubimg> {
    return this.http
      .post<DTOSubimg>('/api/v1/subimg', subimg)
      .pipe(catchError(this.handleError));
  }

  updateData(id: number, subimg: DTOPayment): Observable<DTOSubimg> {
    return this.http
      .patch<DTOSubimg>(`/api/v1/subimg/${id}`, subimg)
      .pipe(catchError(this.handleError));
  }

  deleteDataById(id: number): Observable<DTOSubimg> {
    return this.http
      .delete<DTOSubimg>(`/api/v1/subimg/${id}`)
      .pipe(catchError(this.handleError));
  }

  private handleError(error: any) {
    console.error('An error occurred:', error);
    return throwError(
      () => new Error('Something went wrong. Please try again later.')
    );
  }
}
