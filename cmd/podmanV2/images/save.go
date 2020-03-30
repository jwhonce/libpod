package images

import (
	"context"
	"os"
	"strings"

	"github.com/containers/libpod/cmd/podmanV2/parse"
	"golang.org/x/crypto/ssh/terminal"

	"github.com/containers/libpod/cmd/podmanV2/registry"
	"github.com/containers/libpod/pkg/domain/entities"

	"github.com/containers/libpod/pkg/util"
	"github.com/pkg/errors"
	"github.com/spf13/cobra"
)

const (
	ociManifestDir  = "oci-dir"
	ociArchive      = "oci-archive"
	v2s2ManifestDir = "docker-dir"
	v2s2Archive     = "docker-archive"
)

var validFormats = []string{ociManifestDir, ociArchive, v2s2ManifestDir, v2s2Archive}

var (
	saveDescription = `Save an image to docker-archive or oci-archive on the local machine. Default is docker-archive.`

	saveCommand = &cobra.Command{
		Use:               "save [flags] IMAGE",
		Short:             "Save image to an archive",
		Long:              saveDescription,
		PersistentPreRunE: preRunE,
		RunE:              save,
		Args: func(cmd *cobra.Command, args []string) error {
			if len(args) == 0 {
				return errors.Errorf("need at least 1 argument")
			}
			format, err := cmd.Flags().GetString("format")
			if err != nil {
				return err
			}
			if !util.StringInSlice(format, validFormats) {
				return errors.Errorf("format value must be one of %s", strings.Join(validFormats, " "))
			}
			return nil
		},
		Example: `podman save --quiet -o myimage.tar imageID
  podman save --format docker-dir -o ubuntu-dir ubuntu
  podman save > alpine-all.tar alpine:latest`,
	}
)

var (
	saveOpts entities.ImageSaveOptions
)

func init() {
	registry.Commands = append(registry.Commands, registry.CliCommand{
		Mode:    []entities.EngineMode{entities.ABIMode, entities.TunnelMode},
		Command: saveCommand,
	})
	flags := saveCommand.Flags()
	flags.BoolVar(&saveOpts.Compress, "compress", false, "Compress tarball image layers when saving to a directory using the 'dir' transport. (default is same compression type as source)")
	flags.StringVar(&saveOpts.Format, "format", v2s2Archive, "Save image to oci-archive, oci-dir (directory with oci manifest type), docker-archive, docker-dir (directory with v2s2 manifest type)")
	flags.StringVarP(&saveOpts.Output, "output", "o", "", "Write to a specified file (default: stdout, which must be redirected)")
	flags.BoolVarP(&saveOpts.Quiet, "quiet", "q", false, "Suppress the output")

}

func save(cmd *cobra.Command, args []string) error {
	var (
		tags []string
	)
	if cmd.Flag("compress").Changed && (saveOpts.Format != ociManifestDir && saveOpts.Format != v2s2ManifestDir && saveOpts.Format == "") {
		return errors.Errorf("--compress can only be set when --format is either 'oci-dir' or 'docker-dir'")
	}
	if len(saveOpts.Output) == 0 {
		fi := os.Stdout
		if terminal.IsTerminal(int(fi.Fd())) {
			return errors.Errorf("refusing to save to terminal. Use -o flag or redirect")
		}
		saveOpts.Output = "/dev/stdout"
	}
	if err := parse.ValidateFileName(saveOpts.Output); err != nil {
		return err
	}
	if len(args) > 1 {
		tags = args[1:]
	}
	return registry.ImageEngine().Save(context.Background(), args[0], tags, saveOpts)
}
