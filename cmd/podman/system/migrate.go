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
	migrateDescription = `
        podman system migrate

        Migrate existing containers to a new version of Podman.
`

	migrateCommand = &cobra.Command{
		Use:   "migrate",
		Args:  validate.NoArgs,
		Short: "Migrate containers",
		Long:  migrateDescription,
		Run:   migrate,
	}
)

var (
	migrateOptions entities.SystemMigrateOptions
)

func init() {
	registry.Commands = append(registry.Commands, registry.CliCommand{
		Mode:    []entities.EngineMode{entities.ABIMode},
		Command: migrateCommand,
		Parent:  systemCmd,
	})

	flags := migrateCommand.Flags()
	flags.StringVar(&migrateOptions.NewRuntime, "new-runtime", "", "Specify a new runtime for all containers")
}

func migrate(cmd *cobra.Command, args []string) {
	err := registry.ContainerEngine().SystemMigrate(registry.Context(), migrateOptions, cmd.Flags(), registry.PodmanConfig())
	if err == nil {
		os.Exit(0)
	}
	fmt.Println(err)
	os.Exit(125)
}
