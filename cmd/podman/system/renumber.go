package system

import (
	"fmt"
	"os"

	"github.com/containers/libpod/cmd/podman/registry"
	"github.com/containers/libpod/cmd/podman/validate"
	"github.com/containers/libpod/pkg/domain/entities"
	"github.com/spf13/cobra"
)

var (
	renumberDescription = `
        podman system renumber

        Migrate lock numbers to handle a change in maximum number of locks.
        Mandatory after the number of locks in libpod.conf is changed.
`

	renumberCommand = &cobra.Command{
		Use:   "renumber",
		Args:  validate.NoArgs,
		Short: "Migrate lock numbers",
		Long:  renumberDescription,
		Run:   renumber,
	}
)

func init() {
	registry.Commands = append(registry.Commands, registry.CliCommand{
		Mode:    []entities.EngineMode{entities.ABIMode},
		Command: renumberCommand,
		Parent:  systemCmd,
	})

}
func renumber(cmd *cobra.Command, args []string) {
	err := registry.ContainerEngine().SystemRenumber(registry.Context(), cmd.Flags(), registry.PodmanConfig())
	if err == nil {
		os.Exit(0)
	}
	fmt.Println(err)
	os.Exit(125)
}
