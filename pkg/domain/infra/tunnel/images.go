package tunnel

import (
	"context"
	"os"

	utils2 "github.com/containers/libpod/utils"

	images "github.com/containers/libpod/pkg/bindings/images"
	"github.com/containers/libpod/pkg/domain/entities"
	"github.com/containers/libpod/pkg/domain/utils"
)

func (ir *ImageEngine) Exists(_ context.Context, nameOrId string) (*entities.BoolReport, error) {
	found, err := images.Exists(ir.ClientCxt, nameOrId)
	return &entities.BoolReport{Value: found}, err
}

func (ir *ImageEngine) Delete(ctx context.Context, nameOrId []string, opts entities.ImageDeleteOptions) (*entities.ImageDeleteReport, error) {
	report := entities.ImageDeleteReport{}

	for _, id := range nameOrId {
		results, err := images.Remove(ir.ClientCxt, id, &opts.Force)
		if err != nil {
			return nil, err
		}
		for _, e := range results {
			if a, ok := e["Deleted"]; ok {
				report.Deleted = append(report.Deleted, a)
			}

			if a, ok := e["Untagged"]; ok {
				report.Untagged = append(report.Untagged, a)
			}
		}
	}
	return &report, nil
}

func (ir *ImageEngine) List(ctx context.Context, opts entities.ImageListOptions) ([]*entities.ImageSummary, error) {
	images, err := images.List(ir.ClientCxt, &opts.All, opts.Filters)

	if err != nil {
		return nil, err
	}

	is := make([]*entities.ImageSummary, len(images))
	for i, img := range images {
		hold := entities.ImageSummary{}
		if err := utils.DeepCopy(&hold, img); err != nil {
			return nil, err
		}
		is[i] = &hold
	}
	return is, nil
}

func (ir *ImageEngine) History(ctx context.Context, nameOrId string, opts entities.ImageHistoryOptions) (*entities.ImageHistoryReport, error) {
	results, err := images.History(ir.ClientCxt, nameOrId)
	if err != nil {
		return nil, err
	}

	history := entities.ImageHistoryReport{
		Layers: make([]entities.ImageHistoryLayer, len(results)),
	}

	for i, layer := range results {
		hold := entities.ImageHistoryLayer{}
		_ = utils.DeepCopy(&hold, layer)
		history.Layers[i] = hold
	}
	return &history, nil
}

func (ir *ImageEngine) Prune(ctx context.Context, opts entities.ImagePruneOptions) (*entities.ImagePruneReport, error) {
	results, err := images.Prune(ir.ClientCxt, &opts.All, opts.Filters)
	if err != nil {
		return nil, err
	}

	report := entities.ImagePruneReport{
		Report: entities.Report{
			Id:  results,
			Err: nil,
		},
		Size: 0,
	}
	return &report, nil
}

func (ir *ImageEngine) Save(ctx context.Context, nameOrId string, tags []string, options entities.ImageSaveOptions) error {
	//var f *os.File
	//var err error
	//if options.Format == "oci-dir" || options.Format == "docker-dir" {
	//	f, err = ioutil.TempFile("", "podmansave")
	//	if err == nil {
	//		defer os.Remove(f.Name())
	//	}
	//} else {
	//	_, cherr := os.Stat(options.Output)
	//	if cherr != nil {
	//		if os.IsNotExist(cherr) {
	//			f, err = os.Create(options.Output)
	//		} else {
	//			return cherr
	//		}
	//	} else {
	//		fmt.Println("*******")
	//		f, err = os.Open(options.Output)
	//	}
	//
	//}
	//if err != nil {
	//	_ = f.Close()
	//	return err
	//}
	f, err := os.Create("t")
	if err != nil {
		return err
	}
	f.Close()
	f, err = os.Open("t")
	if err != nil {
		return err
	}
	exErr := images.Export(ir.ClientCxt, nameOrId, f, &options.Format, &options.Compress)
	if err := f.Close(); err != nil {
		return err
	}
	if exErr != nil {
		return exErr
	}
	if options.Format != "oci-dir" && options.Format != "docker-dir" {
		return nil
	}
	return utils2.UntarToFileSystem(options.Output, f, nil)
}
