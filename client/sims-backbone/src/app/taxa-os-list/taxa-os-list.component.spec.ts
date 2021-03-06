import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { TaxaOsListComponent } from './taxa-os-list.component';
import { RouterModule, ActivatedRoute } from '@angular/router';
import { OAuthService } from 'angular-oauth2-oidc';
import { HttpClientModule } from '@angular/common/http';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { createOAuthServiceSpy, ActivatedRouteStub } from 'testing/index.spec';
import { Input, Component } from '@angular/core';

@Component({
  selector: 'app-os-list',
  template: ''
})
export class OsListComponentStub {
  @Input() filter: string;
  @Input() studyName: string;
  @Input() downloadFileName: string;
  @Input() jsonDownloadFileName: string;
}
describe('TaxaOsListComponent', () => {
  let component: TaxaOsListComponent;
  let fixture: ComponentFixture<TaxaOsListComponent>;

  let activatedRoute: ActivatedRouteStub;
  beforeEach(async(() => {

    activatedRoute = new ActivatedRouteStub();

    activatedRoute.setParamMap({
      taxaId: 5877
    });

    TestBed.configureTestingModule({
      imports: [
        RouterModule,
        HttpClientModule,
        HttpClientTestingModule,
      ],
      declarations: [
        TaxaOsListComponent,
        OsListComponentStub
      ],
      providers: [
        { provide: OAuthService, useValue: createOAuthServiceSpy() },
        { provide: ActivatedRoute, useValue: activatedRoute }
      ]
    })
      .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TaxaOsListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
