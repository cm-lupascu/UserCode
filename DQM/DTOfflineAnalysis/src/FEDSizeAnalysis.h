#ifndef FEDSizeAnalysis_H
#define FEDSizeAnalysis_H

/** \class FEDSizeAnalysis
 *  No description available.
 *
 *  $Date: $
 *  $Revision: $
 *  \author G. Cerminara - INFN Torino
 */


#include <FWCore/Framework/interface/EDAnalyzer.h>

#include <string>
#include <vector>

class TFile;
class TNtuple;


class FEDSizeAnalysis : public edm::EDAnalyzer {
public:
  /// Constructor
  FEDSizeAnalysis(const edm::ParameterSet& pset);

  /// Destructor
  virtual ~FEDSizeAnalysis();

  // Operations

protected:

private:
  /// Analyze
  void analyze(const edm::Event& event, const edm::EventSetup& setup);

  // BeginJob
  void beginJob(const edm::EventSetup& setup);

  // EndJob
  void endJob();

  TFile *theFile;
  std::string theRootFileName;
  std::vector<int> feds;
  TNtuple *theNtuple;
  edm::InputTag inputLabel;


};
#endif

