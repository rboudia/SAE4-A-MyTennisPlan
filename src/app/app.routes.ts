import { Routes } from '@angular/router';
import {TournoiComponent} from "./tournoi/tournoi.component";
import {JoueurComponent} from "./joueur/joueur.component";
import {AcceuilComponent} from "./acceuil/acceuil.component"
import { ModifTournoiComponent } from "./modif-tournoi/modif-tournoi.component";
export const routes: Routes = [
  {path:'tournois', component: TournoiComponent},
  {path:'joueurs', component: JoueurComponent},
  {path:'', component: AcceuilComponent},
  {path: 'modifier-tournoi/:id', component: ModifTournoiComponent },
];
