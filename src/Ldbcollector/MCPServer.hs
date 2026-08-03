{-# LANGUAGE OverloadedStrings #-}

module Ldbcollector.MCPServer
  ( serveMCPHttp,
  )
where

import Control.Exception (SomeException, catch)
import Data.ByteString.Lazy qualified as BL
import Data.Vector qualified as V
import Ldbcollector.Model
import MCP.Server qualified as MCP
import MCP.Server.Types qualified as MCP
import System.Environment qualified as Env

-- | Run the MCP server over HTTP (Streamable HTTP transport).
-- Takes a fully-loaded LicenseGraph and serves it on the configured port.
serveMCPHttp :: LicenseGraph -> IO ()
serveMCPHttp licenseGraph = do
  mcpPort <- maybe 3001 read <$> Env.lookupEnv "MCP_PORT"
  putStrLn $ "MCP_PORT=" ++ show mcpPort
  let config =
        MCP.HttpConfig
          { MCP.httpPort = mcpPort,
            MCP.httpHost = "localhost",
            MCP.httpEndpoint = "/mcp",
            MCP.httpVerbose = False
          }
  MCP.runMcpServerHttpWithConfig config mcpServerInfo (mcpHandlers licenseGraph)

mcpServerInfo :: MCP.McpServerInfo
mcpServerInfo =
  MCP.McpServerInfo
    { MCP.serverName = "ldbcollector",
      MCP.serverVersion = "0.1.0.0",
      MCP.serverInstructions =
        "License database collector MCP server. "
          <> "Use the lookup_license_names tool to find alternative names for a license."
    }

mcpHandlers :: LicenseGraph -> MCP.McpServerHandlers IO
mcpHandlers licenseGraph =
  MCP.McpServerHandlers
    { MCP.prompts = Nothing,
      MCP.resources = Nothing,
      MCP.tools = Just (toolListHandler, toolCallHandler licenseGraph)
    }

-- | List all available tools.
toolListHandler :: MCP.ToolListHandler IO
toolListHandler =
  pure
    [ MCP.ToolDefinition
        { MCP.toolDefinitionName = "lookup_license_names",
          MCP.toolDefinitionDescription =
            "Given a license name, returns all known alternative names "
              <> "(same licenses) and related names (hints/imprecise matches) "
              <> "from the license database.",
          MCP.toolDefinitionInputSchema =
            MCP.InputSchemaDefinitionObject
              { MCP.properties =
                  [ ( "licenseName",
                      MCP.InputSchemaDefinitionProperty
                        { MCP.propertyType = "string",
                          MCP.propertyDescription =
                            "The license name to look up, e.g. 'MIT', 'Apache-2.0', 'spdx:GPL-3.0-only'"
                        }
                    )
                  ],
                MCP.required = ["licenseName"]
              },
          MCP.toolDefinitionTitle = Just "Lookup License Names"
        }
    ]

-- | Handle tool calls by dispatching on tool name.
toolCallHandler :: LicenseGraph -> MCP.ToolCallHandler IO
toolCallHandler licenseGraph toolName args =
  case toolName of
    "lookup_license_names" -> lookupLicenseNames licenseGraph args
    _ -> pure $ Left $ MCP.UnknownTool toolName

-- | Look up alternative names for a license.
lookupLicenseNames :: LicenseGraph -> [(MCP.ArgumentName, MCP.ArgumentValue)] -> IO (Either MCP.Error MCP.Content)
lookupLicenseNames licenseGraph args =
  case lookup "licenseName" args of
    Nothing -> pure $ Left $ MCP.MissingRequiredParams "licenseName"
    Just licenseNameText -> do
      let ln = fromText licenseNameText
          needle = LGName ln
      result <- lookupCluster licenseGraph needle
      case result of
        Nothing ->
          pure . Right . MCP.ContentText $
            "No license found for: " <> licenseNameText
        Just cluster ->
          let jsonText = (bsToText . BL.toStrict . encodePretty) cluster
           in pure . Right . MCP.ContentText $ jsonText

-- | Run the graph focus algorithm to compute the LicenseNameCluster
-- for a given license graph node.
lookupCluster :: LicenseGraph -> LicenseGraphNode -> IO (Maybe LicenseNameCluster)
lookupCluster licenseGraph needle =
  ( do
      (result, _) <-
        runLicenseGraphM' licenseGraph $
          focus mempty (V.singleton needle) $
            \(needleNames, sameNames, otherNames, _statements) ->
              getLicenseNameClusterM (needleNames, sameNames, otherNames)
      pure (Just result)
  )
    `catch` (\(_ :: SomeException) -> pure Nothing)
