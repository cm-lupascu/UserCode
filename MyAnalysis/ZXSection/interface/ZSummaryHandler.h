#ifndef zz2l2nusummaryhandler_h
#define zz2l2nusummaryhandler_h

#if !defined(__CINT__) || defined(__MAKECINT__)

#include <string.h>
#include <iomanip>
#include <iostream>
#include <fstream>
#include <set>
#include <cmath>

#include "TTree.h"

#endif

#define MAXPARTICLES 25
struct ZZ2l2nuSummary_t
{
  enum HiggsPtWeights{ hKfactor, hKfactor_renUp, hKfactor_renDown, hKfactor_factUp, hKfactor_factDown };
  enum LeptonInfo { PtError, NeutralHadronIso, ChargedHadronIso, PhotonIso };
  enum JetInfo { TCHE, TCHP, SSVHE, SSVHP };

  Int_t run,lumi,BXId,event;
  Int_t cat;
  Bool_t hasTrigger;

  //gen level 
  Int_t nvtx, ngenITpu,ngenOOTpu;
  Float_t weight, normWeight, hptWeights[5];
  Float_t rho;
  Float_t pthat,genWeight, qscale, x1,x2;
  Int_t id1,id2;
  Int_t pass;

  //dilepton
  Float_t l1_px  ,l1_py  ,l1_pz  ,l1_en, l1_ptErr, l1_iso1, l1_iso2, l1_iso3; Int_t l1_id, l1_genid;
  Float_t l2_px  ,l2_py  ,l2_pz  ,l2_en, l2_ptErr, l2_iso1, l2_iso2, l2_iso3; Int_t l2_id, l2_genid;

  //other leptons
  Int_t ln;
  Float_t ln_px[MAXPARTICLES],ln_py[MAXPARTICLES],ln_pz[MAXPARTICLES],ln_en[MAXPARTICLES], ln_ptErr[MAXPARTICLES], ln_iso1[MAXPARTICLES], ln_iso2[MAXPARTICLES], ln_iso3[MAXPARTICLES]; Int_t ln_id[MAXPARTICLES], ln_genid[MAXPARTICLES];

  //jets
  Int_t jn;
  Float_t jn_px[MAXPARTICLES],jn_py[MAXPARTICLES],jn_pz[MAXPARTICLES],jn_en[MAXPARTICLES], jn_btag1[MAXPARTICLES], jn_btag2[MAXPARTICLES], jn_btag3[MAXPARTICLES], jn_btag4[MAXPARTICLES];  
  Bool_t jn_vtxAssoc[MAXPARTICLES]; 
  Int_t jn_genid[MAXPARTICLES];

  //primary vertex
  Float_t vtx_px  ,vtx_py  ,vtx_pz  ,vtx_en;
  
  //met types
  Float_t met1_phi ,met1_pt;
  Float_t met2_phi ,met2_pt;
  Float_t met3_phi ,met3_pt;
  Float_t met4_phi ,met4_pt;
  Float_t met5_phi ,met5_pt;
  Float_t met6_phi ,met6_pt;
  Float_t met7_phi ,met7_pt;

  //gamma candidate
  Float_t g_px  , g_py  , g_pz  , g_en, g_iso1, g_iso2, g_iso3, g_sihih, g_sipip, g_r9, g_hoe, g_eop;

  //gen level event
  Float_t h_px, h_py, h_pz, h_en;
  Int_t nmcparticles;
  Float_t mc_px[MAXPARTICLES],mc_py[MAXPARTICLES],mc_pz[MAXPARTICLES],mc_en[MAXPARTICLES]; Int_t mc_id[MAXPARTICLES];
};

class ZSummaryHandler{
 public:

  //c/dtor
  ZSummaryHandler();
  ~ZSummaryHandler();

  //current event
  ZZ2l2nuSummary_t evSummary_;
  ZZ2l2nuSummary_t &getEvent() { return evSummary_; }
  
  //write mode
  bool initTree(TTree *t,bool needsToRecreate=true);
  void fillTree();

  //read mode
  bool attachToTree(TTree *t);
  Int_t getEntry(int ientry)
  {
    if(t_) return t_ -> GetEntry(ientry); 
    else return -2;
  }

  int getEntries() { return (t_ ? t_->GetEntriesFast() : 0); }

  //getter
  TTree *getTree() { return t_; }

 private:

  //the tree
  TTree *t_;
};

#endif
